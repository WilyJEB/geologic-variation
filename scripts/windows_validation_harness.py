"""Offline harness preparation. No entry point, DLL loading, or process bootstrap.

Control roles are stepped independently by an injected scheduler/transport. Native
transport/bootstrap is deliberately unavailable: see the review stopping point.
Never pass sampler callbacks, locks, queues or evidence writers to Control.
"""
import ctypes as C
import json

QUERY = 0x1000
SYNC = 0x100000
TERMINATE = 1
DUP = 0x40
JOB_CONTROL = 0x0004 | 0x0008  # QUERY | TERMINATE
PARENT_CONTROL = QUERY | SYNC | TERMINATE


class Invalid(RuntimeError):
    pass


class Startup(C.Structure):
    _fields_ = [('cb', C.c_uint32), ('reserved', C.c_wchar_p),
                ('desktop', C.c_wchar_p), ('title', C.c_wchar_p)] + [
                    (n, C.c_uint32) for n in ('x', 'y', 'xs', 'ys', 'xc', 'yc', 'fill', 'flags')
                ] + [('show', C.c_uint16), ('reserved_size', C.c_uint16),
                     ('reserved_bytes', C.c_void_p), ('stdin', C.c_void_p),
                     ('stdout', C.c_void_p), ('stderr', C.c_void_p)]


class StartupEx(C.Structure):
    _fields_ = [('startup', Startup), ('attributes', C.c_void_p)]


class ProcessInfo(C.Structure):
    _fields_ = [('process', C.c_void_p), ('thread', C.c_void_p),
                ('pid', C.c_uint32), ('tid', C.c_uint32)]


class CreationBindings:
    """Injected kernel functions only; construction never locates/loads a DLL.

    Caller provides already-bound functions and a WinError-producing require.
    Failure to delete attributes after successful creation still returns handles
    via acquire, so evidence/logging cannot lose ownership of a suspended target.
    """
    signatures = {
        'InitializeProcThreadAttributeList': ([C.c_void_p, C.c_uint32, C.c_uint32, C.POINTER(C.c_size_t)], C.c_int32),
        'UpdateProcThreadAttribute': ([C.c_void_p, C.c_uint32, C.c_size_t, C.c_void_p, C.c_size_t, C.c_void_p, C.c_void_p], C.c_int32),
        'DeleteProcThreadAttributeList': ([C.c_void_p], None),
        'CreateProcessW': ([C.c_wchar_p, C.c_wchar_p, C.c_void_p, C.c_void_p, C.c_int32,
                            C.c_uint32, C.c_void_p, C.c_wchar_p, C.c_void_p, C.POINTER(ProcessInfo)], C.c_int32),
        'DuplicateHandle': ([C.c_void_p, C.c_void_p, C.c_void_p, C.POINTER(C.c_void_p),
                             C.c_uint32, C.c_int32, C.c_uint32], C.c_int32),
    }

    def __init__(self, kernel, require, last_error):
        self.k, self.require, self.last_error = kernel, require, last_error
        for name, (args, result) in self.signatures.items():
            f = getattr(kernel, name)
            f.argtypes, f.restype = args, result

    def atomic(self, job, executable, command_line, cwd, acquire):
        size = C.c_size_t()
        # Documented two-call sizing, not a failed-case retry. ERROR_INSUFFICIENT_BUFFER.
        ok = self.k.InitializeProcThreadAttributeList(None, 1, 0, C.byref(size))
        if ok or self.last_error() != 122 or not 0 < size.value <= 65536:
            raise Invalid('attribute sizing failed')
        storage = C.create_string_buffer(size.value)
        self.require(self.k.InitializeProcThreadAttributeList(storage, 1, 0, C.byref(size)))
        try:
            jobs = (C.c_void_p * 1)(job)
            self.require(self.k.UpdateProcThreadAttribute(storage, 0, 0x0002000D,
                         jobs, C.sizeof(jobs), None, None))  # JOB_LIST
            startup, info = StartupEx(), ProcessInfo()
            startup.startup.cb = C.sizeof(startup)
            startup.attributes = C.cast(storage, C.c_void_p)
            command = C.create_unicode_buffer(command_line)
            self.require(self.k.CreateProcessW(executable, command, None, None,
                         False, 0x00080004, None, cwd, C.byref(startup), C.byref(info)))
            # EXTENDED_STARTUPINFO_PRESENT | CREATE_SUSPENDED, no breakaway/inheritance.
            acquire(info.process, info.thread)
        finally:
            self.k.DeleteProcThreadAttributeList(storage)

    def pull(self, source_process, source_handle, receiver_process, rights, acquire):
        result = C.c_void_p()
        self.require(self.k.DuplicateHandle(source_process, source_handle, receiver_process,
                     C.byref(result), rights, False, 0))
        # Value is valid ONLY in receiver. This callback runs there and cannot log.
        acquire(result.value)
        return result.value


class Owner:
    """One table per process. acquire is nonblocking and does not persist evidence."""
    def __init__(self, api):
        self.api, self.handles = api, {}
        self.closed = []

    def acquire(self, label, handle):
        if label in self.handles or not handle or handle in self.handles.values():
            raise Invalid('invalid/repeated acquisition')
        self.handles[label] = handle

    def close(self):
        errors = []
        while self.handles:
            label, handle = self.handles.popitem()
            self.closed.append((label, handle))  # consume even if CloseHandle fails
            try:
                self.api.close(handle)
            except BaseException as error:
                errors.append(repr(error))
        return errors


class Control:
    """Independent watchdog or surviving controller role, never a sampler thread.

    Receiver pulls duplicates into its own process, owns before ACK. Its polling
    loop has no transport read or evidence write. Arm completes before this loop
    starts. Parent transfers require a separate worker; they never mutate the two
    stable control handles. Join that worker before closing its ownership table.
    """
    def __init__(self, api, clock, deadline):
        self.api, self.clock, self.deadline = api, clock, deadline
        self.owner = Owner(api)
        self.armed = False
        self.fired = False

    def arm(self, pull):
        if self.armed or self.owner.handles:
            raise Invalid('arm once')
        # Transport must run these receiver-side, with retained source process
        # handles having PROCESS_DUP_HANDLE. No PID lookup, push or remote close.
        pull('job', JOB_CONTROL, lambda h: self.owner.acquire('job', h))
        pull('peer', SYNC, lambda h: self.owner.acquire('peer', h))
        pull('sampler', SYNC, lambda h: self.owner.acquire('sampler', h))
        if set(self.owner.handles) != {'job', 'peer', 'sampler'}:
            raise Invalid('ownership ACK missing')
        self.armed = True
        return 'armed'

    def parent(self, pull):
        if not self.armed or self.fired or 'parent' in self.owner.handles:
            raise Invalid('parent handoff rejected')
        pull('parent', PARENT_CONTROL, lambda h: self.owner.acquire('parent', h))
        if self.fired or 'parent' not in self.owner.handles:
            raise Invalid('parent ownership ACK missing')
        return 'parent-owned'

    def step(self, interrupted=False):
        if not self.armed or self.fired:
            return None
        reason = None
        try:
            if interrupted:
                reason = 'interruption'
            elif self.clock() >= self.deadline:
                reason = 'deadline'
            elif self.api.wait(self.owner.handles['peer']):
                reason = 'peer-death'
            elif self.api.wait(self.owner.handles['sampler']):
                reason = 'sampler-death'
        except BaseException:
            reason = 'peer-wait-failed'
        if reason is None:
            return None
        self.fired = True
        errors = []
        # No callback, sink, lock, queue or sampler reference precedes these calls.
        for op, label in [('terminate_job', 'job')]:
            try:
                getattr(self.api, op)(self.owner.handles[label])
            except BaseException as error:
                errors.append(repr(error))
        return dict(reason=reason, at=self.clock(), errors=errors, cleanup_verified=False)


class Wiring:
    """Controller preparation sequence. All external effects injected/mocked.

    A native bootstrap/transport implementation is intentionally NOT supplied.
    Those ports may not be replaced with same-thread watchdog calls at runtime.
    """
    def __init__(self, api, transport, owner, job, clock, creation_deadline):
        self.api, self.transport, self.owner, self.job = api, transport, owner, job
        self.clock, self.creation_deadline = clock, creation_deadline
        self.ready = False
        self.started = False

    def start(self, argv):
        if self.started:
            raise Invalid('no retries')
        self.started = True
        try:
            # Includes receiver-owned retained job and exact controller handle.
            if self.transport.arm_watchdog() != 'armed':
                raise Invalid('watchdog not ready')
            if self.clock() >= self.creation_deadline or self.transport.watchdog_dead():
                raise Invalid('readiness expired')
            def acquire(process, thread):
                self.owner.acquire('parent', process)
                self.owner.acquire('thread', thread)
            self.api.atomic(self.job, argv, acquire)
            parent = self.owner.handles['parent']
            identity = self.api.identity(parent)
            if not self.api.member(parent, self.job):
                raise Invalid('atomic membership not verified')
            path = self.api.path(parent)
            if self.transport.parent_to_watchdog(parent) != 'parent-owned':
                raise Invalid('parent ACK missing')
            if self.clock() >= self.creation_deadline or self.transport.watchdog_dead():
                raise Invalid('watchdog died/readiness expired')
            self.api.resume(self.owner.handles['thread'])
            self.ready = True
            return dict(identity=identity, path=path, authored_argv=list(argv))
        except BaseException:
            # Includes lost ACK, API failure, interrupt and evidence-independent cleanup.
            try:
                self.api.terminate_job(self.job)
            finally:
                self.ready = False
            raise


def verify_cleanup(api, job, known_handles, clock, deadline):
    """One successful observation, never termination-return or close as proof."""
    result = dict(complete=False, members=None, accounting=None, waits=[], errors=[])
    try:
        if clock() >= deadline:
            raise Invalid('cleanup deadline')
        result['members'] = api.members(job)
        result['accounting'] = api.accounting(job)
        for h in known_handles:
            result['waits'].append(dict(handle=h, signaled=api.wait(h)))
        result['complete'] = (result['members'] == [] and result['accounting']['active'] == 0
                              and all(w['signaled'] is True for w in result['waits'])
                              and clock() < deadline)
    except BaseException as error:
        result['errors'].append(repr(error))
    return result


class DurableRows:
    """Injected append/flush/fsync; no filesystem opened on import or construction.

    Final complete record is emitted only by a later verifier. Partial/truncated
    files are retained as-is. Disk failure is sticky; control uses no writer.
    """
    def __init__(self, stream, sync):
        self.stream, self.sync = stream, sync
        self.failed = False

    def append(self, row):
        if self.failed:
            raise Invalid('durability previously failed')
        try:
            encoded = json.dumps(row, sort_keys=True) + '\n'
            if self.stream.write(encoded) != len(encoded):
                raise Invalid('short evidence write')
            self.stream.flush()
            self.sync()
        except BaseException:
            self.failed = True
            raise


def check_evidence(rows, known_handles):
    """Conservative offline consistency check, not native acceptance.

    Missing final record, truncated JSON, errors, missing API ends and incomplete
    cleanup fail. Caller retains raw bytes; never repairs or invents rows.
    """
    try:
        if not rows or rows[0]['kind'] != 'case-start' or rows[-1]['kind'] != 'case-end':
            return False
        if rows[-1]['complete'] is not True:
            return False
        starts, ends = {}, {}
        for row in rows:
            if row.get('error') or row.get('complete') is False:
                return False
            if row['kind'] in ('api-start', 'api-end'):
                table = starts if row['kind'] == 'api-start' else ends
                key = (row['role'], row['sequence'])
                if key in table:
                    return False
                table[key] = row
        if not starts or set(starts) != set(ends):
            return False
        if any(ends[k]['api'] != v['api'] or ends[k]['monotonic'] < v['monotonic']
               for k, v in starts.items()):
            return False
        cleanup = [r for r in rows if r['kind'] == 'cleanup']
        if len(cleanup) != 1:
            return False
        row = cleanup[0]
        return (row['complete'] is True and row['members'] == [] and row['accounting']['active'] == 0
                and not row['errors'] and row['monotonic'] < row['deadline']
                and set(w['handle'] for w in row['waits']) == set(known_handles)
                and len(row['waits']) == len(set(known_handles))
                and all(w['signaled'] is True for w in row['waits']))
    except (KeyError, TypeError, ValueError):
        return False
