"""Standalone preparation; no entry point, launcher dependency or import-time OS calls.

Explicit WindowsAPI() construction loads DLLs. Monitor takes owned handles from a
future controller; it never creates a process or reopens a known identity to kill it.
All evidence callbacks must durably append before returning (future harness duty).
"""
import ctypes as C
import time

# Fixed Windows ABI types, also inspectable on non-Windows test hosts.
DWORD = C.c_uint32
HANDLE = C.c_void_p
SIZE = C.c_size_t
BOOL = C.c_int32


class Accounting(C.Structure):
    _fields_ = [(n, C.c_int64) for n in ('user', 'kernel', 'period_user', 'period_kernel')] + [
        (n, DWORD) for n in ('faults', 'total', 'active', 'terminated')]


class Memory(C.Structure):
    _fields_ = [('cb', DWORD), ('faults', DWORD)] + [(n, SIZE) for n in (
        'peak_ws', 'ws', 'peak_paged', 'paged', 'peak_nonpaged', 'nonpaged', 'pagefile', 'peak_pagefile')]


class BasicLimits(C.Structure):
    _fields_ = [('process_time', C.c_int64), ('job_time', C.c_int64), ('flags', DWORD),
                ('min_ws', SIZE), ('max_ws', SIZE), ('active', DWORD), ('affinity', SIZE),
                ('priority', DWORD), ('scheduling', DWORD)]


class Limits(C.Structure):
    _fields_ = [('basic', BasicLimits), ('io', C.c_uint64 * 6)] + [
        (n, SIZE) for n in ('process_memory', 'job_memory', 'peak_process', 'peak_job')]


class Incomplete(RuntimeError):
    pass


class WindowsAPI:
    """Documented APIs only. No creation, shell, CIM, tracing or notification path."""
    def __init__(self):
        import os
        if os.name != 'nt':
            raise RuntimeError('Windows only; construction is native execution')
        self.k = C.WinDLL('kernel32', use_last_error=True)
        signatures = {
            'CreateJobObjectW': ([C.c_void_p, C.c_wchar_p], HANDLE),
            'SetInformationJobObject': ([HANDLE, C.c_int, C.c_void_p, DWORD], BOOL),
            'QueryInformationJobObject': ([HANDLE, C.c_int, C.c_void_p, DWORD, C.c_void_p], BOOL),
            'OpenProcess': ([DWORD, BOOL, DWORD], HANDLE),
            'GetProcessId': ([HANDLE], DWORD),
            'GetProcessTimes': ([HANDLE] + [C.c_void_p] * 4, BOOL),
            'QueryFullProcessImageNameW': ([HANDLE, DWORD, C.c_wchar_p, C.POINTER(DWORD)], BOOL),
            'IsProcessInJob': ([HANDLE, HANDLE, C.POINTER(BOOL)], BOOL),
            'WaitForSingleObject': ([HANDLE, DWORD], DWORD),
            'GetExitCodeProcess': ([HANDLE, C.POINTER(DWORD)], BOOL),
            'K32GetProcessMemoryInfo': ([HANDLE, C.c_void_p, DWORD], BOOL),
            'AssignProcessToJobObject': ([HANDLE, HANDLE], BOOL),
            'ResumeThread': ([HANDLE], DWORD),
            'TerminateJobObject': ([HANDLE, DWORD], BOOL),
            'TerminateProcess': ([HANDLE, DWORD], BOOL),
            'CloseHandle': ([HANDLE], BOOL),
        }
        for name, (args, result) in signatures.items():
            f = getattr(self.k, name)
            f.argtypes, f.restype = args, result

    @staticmethod
    def require(ok):
        if not ok:
            raise C.WinError(C.get_last_error())
        return ok

    def create_job(self):
        h = self.require(self.k.CreateJobObjectW(None, None))
        try:
            limits = Limits()
            limits.basic.flags = 0x2000  # KILL_ON_JOB_CLOSE; neither breakaway flag.
            self.require(self.k.SetInformationJobObject(h, 9, C.byref(limits), C.sizeof(limits)))
            return h
        except BaseException:
            self.close(h)
            raise

    def members(self, job):
        # One bounded query; ERROR_MORE_DATA is an error, never a truncated success.
        data = C.create_string_buffer(8 + 256 * C.sizeof(SIZE))
        self.require(self.k.QueryInformationJobObject(job, 3, data, len(data), None))
        assigned, count = (DWORD * 2).from_buffer(data)
        if assigned != count or count > 256:
            raise Incomplete('job list overflow/inconsistent count')
        return list((SIZE * count).from_buffer(data, 8))

    def accounting(self, job):
        a = Accounting()
        self.require(self.k.QueryInformationJobObject(job, 1, C.byref(a), C.sizeof(a), None))
        return dict(total=a.total, active=a.active, terminated=a.terminated)

    def open(self, pid):
        # Modern Windows: limited query suffices for times/path/memory; synchronize for waits.
        return self.require(self.k.OpenProcess(0x1000 | 0x100000, False, pid))

    def identity(self, h):
        pid = self.require(self.k.GetProcessId(h))
        creation, exit_time, kernel, user = (C.c_uint64() for _ in range(4))
        self.require(self.k.GetProcessTimes(h, C.byref(creation), C.byref(exit_time), C.byref(kernel), C.byref(user)))
        return pid, creation.value  # raw 64-bit FILETIME, no float conversion

    def path(self, h):
        buf, count = C.create_unicode_buffer(32768), DWORD(32768)
        self.require(self.k.QueryFullProcessImageNameW(h, 0, buf, C.byref(count)))
        return buf.value

    def member(self, h, job):
        result = BOOL()
        self.require(self.k.IsProcessInJob(h, job, C.byref(result)))
        return bool(result.value)

    def wait(self, h):
        result = self.k.WaitForSingleObject(h, 0)
        if result == 0xffffffff:
            raise C.WinError(C.get_last_error())
        if result not in (0, 258):
            raise Incomplete('unexpected process wait result')
        return result == 0

    def exit_code(self, h):
        result = DWORD()
        self.require(self.k.GetExitCodeProcess(h, C.byref(result)))
        return result.value  # 259 is a valid exit after a signaled wait.

    def memory(self, h):
        result = Memory()
        result.cb = C.sizeof(result)
        self.require(self.k.K32GetProcessMemoryInfo(h, C.byref(result), result.cb))
        return result.ws

    def assign(self, job, h):
        self.require(self.k.AssignProcessToJobObject(job, h))

    def resume(self, thread):
        previous = self.k.ResumeThread(thread)
        if previous == 0xffffffff:
            raise C.WinError(C.get_last_error())
        if previous != 1:
            raise Incomplete('expected exactly one suspension')

    def terminate_job(self, job):
        self.require(self.k.TerminateJobObject(job, 1))

    def terminate_process(self, h):
        self.require(self.k.TerminateProcess(h, 1))

    def close(self, h):
        self.require(self.k.CloseHandle(h))


class Monitor:
    """Single sampler owner. Never share its handles with a concurrent closer.

    deadline is cooperative only. Future independent watchdog uses duplicate handles
    with separate ownership, no Python lock/IPC roundtrip through this object.
    """
    def __init__(self, api, job, emit, deadline, clock=time.monotonic, wall=time.time):
        self.api, self.job, self.emit = api, job, emit
        self.deadline, self.clock, self.wall = deadline, clock, wall
        self.owned = [job]
        self.known = {}
        self.process_handles = []
        self.failed = False
        self.closed = False
        self.sequence = 0
        self.emit(dict(kind='ownership', handle=job))

    def call(self, operation, *args):
        start = self.clock()
        row = dict(sequence=self.sequence, api=operation, args=list(args),
                   start=start, unix=self.wall(), complete=False)
        self.sequence += 1
        # Start record survives a stuck API; sink failures also abort inspection.
        self.emit(dict(row, phase='start'))
        try:
            value = getattr(self.api, operation)(*args)
            if operation == 'open':
                # Own acquired resources before the completion sink can fail.
                self.own(value)
                self.process_handles.append(value)
            row.update(result=value, complete=True)
            return value
        except BaseException as error:
            self.failed = True
            row.update(error=repr(error), winerror=getattr(error, 'winerror', None))
            raise
        finally:
            row.update(end=self.clock(), phase='end')
            self.emit(row)

    def guard(self):
        if self.closed or self.failed or self.clock() >= self.deadline:
            self.failed = True
            self.emit(dict(kind='inspection-stop', complete=False, unix=self.wall(),
                           monotonic=self.clock(), reason='closed, previous failure or cooperative deadline'))
            raise Incomplete('closed, previous failure or cooperative deadline')

    def own(self, h):
        if h in self.owned:
            raise Incomplete('duplicate handle ownership')
        self.owned.append(h)
        self.emit(dict(kind='ownership', handle=h))
        return h

    def accept(self, h, expected_pid=None):
        identity = tuple(self.call('identity', h))
        if expected_pid is not None and identity[0] != expected_pid:
            raise Incomplete('opened PID mismatch')
        if not self.call('member', h, self.job):
            raise Incomplete('opened process is not in retained job')
        path = self.call('path', h)
        if identity in self.known:
            raise Incomplete('duplicate exact identity')
        self.known[identity] = dict(handle=h, path=path, command=None, parent=None)
        return identity

    def adopt_suspended(self, process, thread, authored_argv):
        """Transfer both handles even on failure; caller must finally cleanup/close.

        Future watchdog must acknowledge its own exact-parent duplicate BEFORE this
        function is entered. This function does not start or wire that watchdog.
        """
        self.own(process)
        self.process_handles.append(process)
        self.own(thread)
        assigned = False
        try:
            self.guard()
            identity = self.call('identity', process)
            path = self.call('path', process)
            self.call('assign', self.job, process)
            assigned = True
            if not self.call('member', process, self.job):
                raise Incomplete('assignment membership unverified')
            self.known[tuple(identity)] = dict(handle=process, path=path,
                authored_argv=list(authored_argv), command=None, parent=None)
            self.guard()
            self.call('resume', thread)
        except BaseException:
            self.failed = True
            # Retained handle, never a PID. Assignment may not have happened.
            try:
                self.call('terminate_job', self.job) if assigned else self.call('terminate_process', process)
            finally:
                self.call('wait', process)  # false remains explicitly incomplete
            raise

    def sample(self):
        self.guard()
        row = dict(kind='sample', complete=False, memory_bytes=None, processes=[])
        try:
            before = self.call('members', self.job)
            if len(before) != len(set(before)):
                raise Incomplete('duplicate member PID')
            for pid in before:
                # A retained unsignaled handle identifies the live process; exited ones may coexist
                # with a NEW identity having the same PID. Never overwrite the old key.
                live = False
                for key, entry in list(self.known.items()):
                    if key[0] == pid and not self.call('wait', entry['handle']):
                        if not self.call('member', entry['handle'], self.job):
                            raise Incomplete('retained membership mismatch')
                        live = True
                if not live:
                    h = self.call('open', pid)
                    self.accept(h, pid)
            after = self.call('members', self.job)
            if sorted(before) != sorted(after):
                raise Incomplete('enumeration/open reconciliation race')
            total = 0
            for key, entry in self.known.items():
                self.guard()
                h = entry['handle']
                exited = self.call('wait', h)
                detail = dict(identity=list(key), exited=exited, memory_bytes=None, exit_code=None)
                row['processes'].append(detail)
                if exited:
                    detail['exit_code'] = self.call('exit_code', h)
                elif key[0] in after:
                    detail['memory_bytes'] = self.call('memory', h)
                    total += detail['memory_bytes']
                else:
                    raise Incomplete('live retained handle missing from job list')
            self.guard()
            row.update(complete=True, memory_bytes=total)
            return row
        except BaseException as error:
            self.failed = True
            row['error'] = repr(error)
            raise
        finally:
            self.emit(row)

    def cleanup(self, cleanup_deadline, pause=time.sleep):
        """Cooperative cleanup; independent watchdog is required for blocked calls.

        Unknown queries never become absence. Observation failure remains sticky even
        if a subsequent cleanup poll proves containment. No discovery during cleanup.
        """
        result = dict(kind='cleanup', complete=False, observation_complete=not self.failed)
        errors = []
        try:
            try:
                self.call('terminate_job', self.job)
            except BaseException as error:
                errors.append(repr(error))
            while self.clock() < cleanup_deadline:
                try:
                    members = self.call('members', self.job)
                    accounting = self.call('accounting', self.job)
                    waits = [self.call('wait', h) for h in self.process_handles]
                    result.update(members=members, accounting=accounting, waits=waits)
                    if (not members and accounting['active'] == 0 and all(waits)
                            and self.clock() < cleanup_deadline):
                        result['complete'] = not errors
                        break
                except BaseException as error:
                    errors.append(repr(error))
                    break  # no retry that erases a required-query failure
                pause(min(.05, max(0, cleanup_deadline - self.clock())))
        except BaseException as error:
            errors.append(repr(error))
        finally:
            result.update(errors=errors, deadline_reached=self.clock() >= cleanup_deadline)
            self.emit(result)
        return result

    def close(self):
        """No concurrency with sampler/waits. Failed close is recorded, never retried."""
        self.closed = True
        errors = []
        while self.owned:
            h = self.owned.pop()  # consume ownership BEFORE close, including exceptions
            row = dict(kind='handle-close', handle=h, start=self.clock(), unix=self.wall(), complete=False)
            try:
                # Cleanup must not depend on a functioning evidence sink.
                self.api.close(h)
                row['complete'] = True
            except BaseException as error:
                errors.append(repr(error))
                row['error'] = repr(error)
            finally:
                row['end'] = self.clock()
                try:
                    self.emit(row)
                except BaseException as error:
                    errors.append(repr(error))
        try:
            self.emit(dict(kind='close', complete=not errors, errors=errors, unix=self.wall()))
        except BaseException:
            return False
        return not errors


def check_trace(rows):
    """Fail-closed mock trace check, NOT native/navigation acceptance.

    Requires full API start/end pairs, complete samples and independent cleanup
    evidence. A successful cleanup cannot erase earlier unknown observations.
    """
    starts, ends = {}, {}
    samples, cleanups, closes, owned, released = [], [], [], [], []
    try:
        for row in rows:
            if row.get('phase') in ('start', 'end'):
                table = starts if row['phase'] == 'start' else ends
                sequence = row['sequence']
                if sequence in table:
                    return False
                table[sequence] = row
            if row.get('kind') == 'sample': samples.append(row)
            if row.get('kind') == 'cleanup': cleanups.append(row)
            if row.get('kind') == 'close': closes.append(row)
            if row.get('kind') == 'ownership': owned.append(row['handle'])
            if row.get('kind') == 'handle-close':
                if not row['complete'] or 'error' in row: return False
                released.append(row['handle'])
        if not starts or set(starts) != set(ends) or sorted(starts) != list(range(len(starts))):
            return False
        for sequence, start in starts.items():
            end = ends[sequence]
            if (not end['complete'] or 'error' in end or start['api'] != end['api']
                    or start['args'] != end['args'] or end['end'] < start['start']):
                return False
        if not samples or len(cleanups) != 1 or len(closes) != 1:
            return False
        if len(owned) != len(set(owned)) or sorted(owned) != sorted(released):
            return False
        for sample in samples:
            if not sample['complete'] or 'error' in sample or sample['memory_bytes'] is None:
                return False
            total = sum(p['memory_bytes'] for p in sample['processes'] if not p['exited'])
            if total != sample['memory_bytes']:
                return False
        cleanup = cleanups[0]
        return bool(cleanup['complete'] and cleanup['observation_complete']
                    and cleanup['members'] == [] and cleanup['accounting']['active'] == 0
                    and all(v is True for v in cleanup['waits']) and not cleanup['errors']
                    and not cleanup['deadline_reached'] and closes[0]['complete']
                    and not closes[0]['errors'])
    except (KeyError, TypeError, ValueError):
        return False


class WatchdogControl:
    """Pure control step for a FUTURE independent process, never a sampler thread.

    Receives its OWN duplicate job/parent/controller handles before resume; no shared
    monitor, locks, sink, queue or sampler callback. Caller supplies absolute deadline.
    This is a testable ownership plan, not a running watchdog or hard deadline proof.
    No evidence writes precede termination. Results must later be durably persisted.
    """
    def __init__(self, api, job, parent, controller, deadline, clock=time.monotonic):
        self.api, self.job, self.parent, self.controller = api, job, parent, controller
        self.deadline, self.clock = deadline, clock
        self.fired = False
        self.closed = False

    def step(self, interrupted=False):
        if self.closed or self.fired:
            return None
        reason = None
        try:
            if interrupted:
                reason = 'interrupted'
            elif self.clock() >= self.deadline:
                reason = 'deadline'
            elif self.api.wait(self.controller):
                reason = 'controller-exited'
        except BaseException:
            reason = 'controller-wait-unknown'
        if reason is None:
            return None
        self.fired = True
        errors = []
        # Parent duplicate covers failure BEFORE job assignment. It is the exact
        # created process, never a PID; terminating an exited handle may fail.
        for operation, h in [('terminate_job', self.job), ('terminate_process', self.parent)]:
            try:
                getattr(self.api, operation)(h)
            except BaseException as error:
                errors.append(dict(api=operation, error=repr(error)))
        return dict(reason=reason, errors=errors, cleanup_verified=False)

    def close(self):
        if self.closed:
            return []
        self.closed = True
        errors = []
        for h in (self.parent, self.controller, self.job):
            try:
                self.api.close(h)
            except BaseException as error:
                errors.append(repr(error))
        return errors
