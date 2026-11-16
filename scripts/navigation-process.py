"""Windows suspended creation in a non-breakaway job; imported without OS calls.

All Windows calls use documented kernel32 APIs. Offline tests inject a fake job.
No process is created until start(). Close kills the job, including descendants
that survive the parent. Query failure is an evidence failure, never absence.
"""
import ctypes as C
from ctypes import wintypes as W
import json
import os
import subprocess
import time
import msvcrt


class Job:
    def __init__(self):
        if os.name != 'nt':
            raise RuntimeError('Windows execution context required')
        self.k = C.WinDLL('kernel32', use_last_error=True)
        signatures = {
            'CreateJobObjectW': ([C.c_void_p, W.LPCWSTR], W.HANDLE),
            'SetInformationJobObject': ([W.HANDLE, C.c_int, C.c_void_p, W.DWORD], W.BOOL),
            'QueryInformationJobObject': ([W.HANDLE, C.c_int, C.c_void_p, W.DWORD, C.c_void_p], W.BOOL),
            'AssignProcessToJobObject': ([W.HANDLE, W.HANDLE], W.BOOL),
            'TerminateJobObject': ([W.HANDLE, W.UINT], W.BOOL),
            'CloseHandle': ([W.HANDLE], W.BOOL),
            'ResumeThread': ([W.HANDLE], W.DWORD),
            'GetExitCodeProcess': ([W.HANDLE, C.POINTER(W.DWORD)], W.BOOL),
            'CreateProcessW': ([W.LPCWSTR, W.LPWSTR, C.c_void_p, C.c_void_p,
                                W.BOOL, W.DWORD, C.c_void_p, W.LPCWSTR,
                                C.c_void_p, C.c_void_p], W.BOOL),
        }
        for name, (args, result) in signatures.items():
            f = getattr(self.k, name); f.argtypes = args; f.restype = result
        self.handle = self.k.CreateJobObjectW(None, None)
        self.require(self.handle)
        # JOBOBJECT_EXTENDED_LIMIT_INFORMATION, layout follows winnt.h.
        class Basic(C.Structure):
            _fields_ = [('process_time', C.c_longlong), ('job_time', C.c_longlong),
                        ('flags', W.DWORD), ('min_ws', C.c_size_t), ('max_ws', C.c_size_t),
                        ('active', W.DWORD), ('affinity', C.c_size_t),
                        ('priority', W.DWORD), ('scheduling', W.DWORD)]
        class Extended(C.Structure):
            _fields_ = [('basic', Basic), ('io', C.c_ulonglong * 6),
                        ('process_memory', C.c_size_t), ('job_memory', C.c_size_t),
                        ('peak_process', C.c_size_t), ('peak_job', C.c_size_t)]
        limits = Extended(); limits.basic.flags = 0x2000  # KILL_ON_JOB_CLOSE; no breakaway
        self.require(self.k.SetInformationJobObject(self.handle, 9, C.byref(limits), C.sizeof(limits)))
        self.process = None
        self.initial_identities = []
        self.start_details = {}

    @staticmethod
    def require(ok):
        if not ok:
            raise C.WinError(C.get_last_error())

    def start(self, cmd, cwd):
        class Startup(C.Structure):
            _fields_ = [('cb', W.DWORD), ('reserved', W.LPWSTR), ('desktop', W.LPWSTR),
                        ('title', W.LPWSTR), ('x', W.DWORD), ('y', W.DWORD),
                        ('xs', W.DWORD), ('ys', W.DWORD), ('xc', W.DWORD),
                        ('yc', W.DWORD), ('fill', W.DWORD), ('flags', W.DWORD),
                        ('show', W.WORD), ('reserved2_size', W.WORD),
                        ('reserved2', C.c_void_p), ('stdin', W.HANDLE),
                        ('stdout', W.HANDLE), ('stderr', W.HANDLE)]
        class Info(C.Structure):
            _fields_ = [('process', W.HANDLE), ('thread', W.HANDLE),
                        ('pid', W.DWORD), ('tid', W.DWORD)]
        startup = Startup(); startup.cb = C.sizeof(startup); info = Info()
        with open(cwd / 'console.log', 'wb') as log, open(os.devnull, 'rb') as null:
            for stream in (log, null):
                os.set_inheritable(stream.fileno(), True)
            startup.flags = 0x100  # STARTF_USESTDHANDLES
            startup.stdout = startup.stderr = msvcrt.get_osfhandle(log.fileno())
            startup.stdin = msvcrt.get_osfhandle(null.fileno())
            self.require(self.k.CreateProcessW(cmd[0], C.create_unicode_buffer(subprocess.list2cmdline(cmd)),
                         None, None, True, 0x4 | 0x08000000, None, str(cwd),
                         C.byref(startup), C.byref(info)))  # suspended + no window
        self.process = info.process; self.pid = info.pid
        self.start_details = dict(pid=info.pid,created_suspended_unix=time.time(),assigned=False,resumed=False)
        try:
            # Capture identity while suspended, before any Java instruction.
            identity = self.identities([info.pid])
            self.initial_identities = identity
            if len(identity) != 1:
                raise RuntimeError('Missing suspended parent identity')
            self.require(self.k.AssignProcessToJobObject(self.handle, info.process))
            self.start_details['assigned'] = True
            if self.k.ResumeThread(info.thread) == 0xffffffff:
                raise C.WinError(C.get_last_error())
            self.start_details['resumed'] = True
            return identity
        except BaseException:
            # Assignment can fail before the process belongs to the job.
            terminate = self.k.TerminateProcess
            terminate.argtypes = [W.HANDLE, W.UINT]; terminate.restype = W.BOOL
            self.require(terminate(info.process, 1))
            raise
        finally:
            self.k.CloseHandle(info.thread)

    def pids(self):
        # Fixed 4096 PID bound; overflow/query failure fails closed.
        data = C.create_string_buffer(8 + 4096 * C.sizeof(C.c_size_t))
        self.require(self.k.QueryInformationJobObject(self.handle, 3, data, len(data), None))
        assigned, count = (W.DWORD * 2).from_buffer(data)
        if assigned != count or count > 4096:
            raise RuntimeError('Incomplete job process list')
        return list((C.c_size_t * count).from_buffer(data, 8))

    def identities(self, pids):
        if not pids:
            return []
        ids = ','.join(str(int(p)) for p in pids)
        script = (f'$ids=@({ids}); Get-CimInstance Win32_Process | '
                  'Where-Object { $ids -contains $_.ProcessId } | '
                  'Select-Object ProcessId,ParentProcessId,CreationDate,CommandLine,WorkingSetSize | ConvertTo-Json -Compress')
        result = subprocess.run(['powershell.exe', '-NoProfile', '-Command', script],
                                capture_output=True, text=True, check=True, timeout=1,
                                creationflags=0x08000000)
        rows = json.loads(result.stdout or '[]')
        return rows if isinstance(rows, list) else [rows]

    def exit_code(self):
        if self.process is None:
            return None
        code = W.DWORD()
        self.require(self.k.GetExitCodeProcess(self.process, C.byref(code)))
        return None if code.value == 259 else code.value

    def cleanup(self, known):
        active = self.pids(); forced = bool(active)
        if active:
            self.require(self.k.TerminateJobObject(self.handle, 1))
        deadline = time.monotonic() + 15
        while (self.pids() or (self.process and self.exit_code() is None)) and time.monotonic() < deadline:
            time.sleep(.1)
        remaining = self.pids()
        queried = self.identities([v['ProcessId'] for v in known.values()])
        alive = {(v['ProcessId'], v['CreationDate']) for v in queried}
        checks = [dict(identity=v, absent=(v['ProcessId'], v['CreationDate']) not in alive)
                  for v in known.values()]
        result = dict(forced=forced, active_before=active, remaining_job_pids=remaining,
                      identity_queries=queried, checks=checks,
                      parent_exit_code=self.exit_code(),
                      job_empty=not remaining, timestamp=time.time())
        return result

    def close(self):
        if self.process:
            self.k.CloseHandle(self.process)
        self.k.CloseHandle(self.handle)
