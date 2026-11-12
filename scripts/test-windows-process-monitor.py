"""Pure fake API tests: constructing WindowsAPI is forbidden, including on Windows."""
import importlib.util
from pathlib import Path
import unittest
import copy
from unittest.mock import patch

with patch('ctypes.WinDLL', create=True, side_effect=AssertionError('native load forbidden')):
    spec = importlib.util.spec_from_file_location('monitor', Path(__file__).with_name('windows_process_monitor.py'))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)


class Clock:
    def __init__(self): self.now = 0
    def __call__(self): return self.now
    def pause(self, seconds): self.now += seconds


class Fake:
    def __init__(self):
        self.ids = {10: (100, 123456789012345678), 20: (200, 9), 21: (200, 10)}
        self.pids = [100]
        self.mapping = {100: 10, 200: 20}
        self.exited = set()
        self.fail = {}
        self.calls = []
        self.member_values = {}
        self.members_sequence = []
        self.code = 259
        self.active = None
        self.total = 1
        self.kill = True

    def __getattribute__(self, name):
        value = object.__getattribute__(self, name)
        if name in ('identity', 'path', 'member', 'assign', 'resume', 'open', 'members',
                    'wait', 'memory', 'exit_code', 'terminate_job', 'terminate_process', 'accounting', 'close'):
            def invoke(*args):
                self.calls.append((name, args))
                if name in self.fail: raise self.fail[name]
                return value(*args)
            return invoke
        return value

    def identity(self, h): return self.ids[h]
    def path(self, h): return 'C:/benign.exe'
    def member(self, h, job): return self.member_values.get(h, True)
    def assign(self, job, h): pass
    def resume(self, thread): pass
    def open(self, pid): return self.mapping[pid]
    def members(self, job):
        return self.members_sequence.pop(0) if self.members_sequence else list(self.pids)
    def wait(self, h): return h in self.exited
    def memory(self, h): return 1000
    def exit_code(self, h): return self.code
    def terminate_job(self, job):
        if self.kill:
            self.pids = []
            self.exited.update(self.ids)
    def terminate_process(self, h): self.exited.add(h)
    def accounting(self, job):
        return dict(active=len(self.pids) if self.active is None else self.active,
                    total=self.total, terminated=len(self.exited))
    def close(self, h): pass


class Tests(unittest.TestCase):
    def setUp(self):
        self.api, self.clock, self.rows = Fake(), Clock(), []
        self.monitor = m.Monitor(self.api, 1, self.rows.append, 10, self.clock, self.clock)

    def adopt(self): self.monitor.adopt_suspended(10, 11, ['benign.exe'])
    def cleanup(self): return self.monitor.cleanup(1, self.clock.pause)

    def test_identity_and_sample(self):
        self.adopt()
        self.assertEqual(list(self.monitor.known), [(100, 123456789012345678)])
        self.assertEqual(self.monitor.sample()['memory_bytes'], 1000)
        self.assertIsNone(next(iter(self.monitor.known.values()))['command'])
        ends = [r for r in self.rows if r.get('phase') == 'end']
        self.assertTrue(all(r['end'] >= r['start'] and r['complete'] for r in ends))

    def test_exit259_requires_wait(self):
        self.adopt()
        self.monitor.sample()
        self.assertFalse(any(n == 'exit_code' for n, _ in self.api.calls))
        self.api.exited.add(10)
        self.api.pids = []
        self.assertEqual(self.monitor.sample()['processes'][0]['exit_code'], 259)

    def test_outliving_child(self):
        self.adopt()
        self.api.pids.append(200)
        self.monitor.sample()
        self.api.exited.add(10)
        self.api.pids = [200]
        self.assertEqual(self.monitor.sample()['memory_bytes'], 1000)
        self.api.kill = False
        self.assertFalse(self.cleanup()['complete'])

    def test_pid_reuse_retains_both_handles(self):
        self.api.pids = [200]
        self.monitor.sample()
        self.api.exited.add(20)
        self.api.mapping[200] = 21
        self.monitor.sample()
        self.assertEqual(set(self.monitor.known), {(200, 9), (200, 10)})
        self.assertEqual(self.monitor.process_handles, [20, 21])

    def test_replacement_outside_job_never_accepted_or_killed(self):
        self.api.pids = [200]
        self.api.mapping[200] = 21
        self.api.member_values[21] = False
        with self.assertRaises(m.Incomplete): self.monitor.sample()
        self.assertEqual(self.monitor.known, {})
        self.cleanup()
        self.assertFalse(any(n == 'terminate_process' for n, _ in self.api.calls))
        self.assertIn(21, self.monitor.process_handles)

    def test_assignment_resume_and_metadata_failure(self):
        for operation in ('identity', 'path', 'assign', 'resume', 'member'):
            with self.subTest(operation=operation):
                self.setUp()
                self.api.fail[operation] = PermissionError('denied')
                with self.assertRaises(PermissionError): self.adopt()
                termination = 'terminate_job' if operation in ('resume', 'member') else 'terminate_process'
                self.assertTrue(any(n == termination for n, _ in self.api.calls))
                self.assertIn(('wait', (10,)), self.api.calls)
                self.assertEqual(self.monitor.process_handles, [10])
                self.monitor.close()
                self.assertCountEqual([a[0] for n, a in self.api.calls if n == 'close'], [1, 10, 11])

    def test_enumeration_open_and_query_failure_matrix(self):
        for operation in ('members', 'open', 'identity', 'path', 'member', 'wait', 'memory'):
            for error in (PermissionError('denied'), OSError('vanished/overflow'), KeyboardInterrupt()):
                with self.subTest(operation=operation, error=type(error).__name__):
                    self.setUp()
                    self.api.fail[operation] = error
                    with self.assertRaises(type(error)): self.monitor.sample()
                    sample = self.rows[-1]
                    self.assertFalse(sample['complete'])
                    self.assertIsNone(sample['memory_bytes'])
                    self.assertTrue(self.monitor.failed)
                    with self.assertRaises(m.Incomplete): self.monitor.sample()
                    self.monitor.close()

    def test_enumeration_race(self):
        self.api.members_sequence = [[100], []]
        with self.assertRaises(m.Incomplete): self.monitor.sample()
        self.assertFalse(self.rows[-1]['complete'])

    def test_partial_memory_is_not_total(self):
        self.api.pids = [100, 200]
        original = self.api.memory
        def memory(h):
            if h == 20: raise OSError('memory unavailable')
            return original(h)
        self.api.memory = memory
        with self.assertRaises(OSError): self.monitor.sample()
        self.assertEqual(self.rows[-1]['processes'][0]['memory_bytes'], 1000)
        self.assertIsNone(self.rows[-1]['memory_bytes'])

    def test_cleanup_required_evidence_matrix(self):
        for operation in ('terminate_job', 'members', 'accounting', 'wait'):
            with self.subTest(operation=operation):
                self.setUp()
                self.adopt()
                self.api.fail[operation] = OSError('failed')
                self.assertFalse(self.cleanup()['complete'])

    def test_job_empty_does_not_replace_wait_or_accounting(self):
        self.adopt()
        self.api.kill = False
        self.api.pids = []
        self.assertFalse(self.cleanup()['complete'])
        self.clock.now = 0
        self.api.exited.add(10)
        self.api.active = 1
        self.assertFalse(self.cleanup()['complete'])

    def test_short_lived_unseen_identity_is_not_invented(self):
        self.adopt()
        self.api.total = 2
        result = self.cleanup()
        self.assertTrue(result['complete'])
        self.assertEqual(len(self.monitor.known), 1)
        self.assertEqual(result['accounting']['total'], 2)

    def test_failure_stays_incomplete_after_containment(self):
        self.adopt()
        self.api.fail['memory'] = OSError('unknown')
        with self.assertRaises(OSError): self.monitor.sample()
        result = self.cleanup()
        self.assertTrue(result['complete'])
        self.assertFalse(result['observation_complete'])

    def test_deadline_interruption_and_close_once(self):
        self.adopt()
        self.clock.now = 10
        with self.assertRaises(m.Incomplete): self.monitor.sample()
        self.assertFalse(self.cleanup()['complete'])
        self.api.fail['close'] = KeyboardInterrupt()
        self.assertFalse(self.monitor.close())
        self.monitor.close()
        self.assertCountEqual([a[0] for n, a in self.api.calls if n == 'close'], [1, 10, 11])

    def test_post_call_deadline_and_sink_failure(self):
        original = self.api.memory
        def late(h):
            value = original(h)
            self.clock.now = 11
            return value
        self.api.memory = late
        with self.assertRaises(m.Incomplete): self.monitor.sample()
        self.assertFalse(self.rows[-1]['complete'])

    def test_abi_sizes_and_no_import_side_effects(self):
        self.assertEqual(m.C.sizeof(m.Accounting), 48)
        self.assertEqual(m.C.sizeof(m.Memory), 8 + 8 * m.C.sizeof(m.SIZE))
        source = Path(m.__file__).read_text()
        self.assertNotIn('subprocess', source)
        self.assertNotIn('powershell', source.lower())

    def test_watchdog_does_not_call_blocked_sampler_or_sink(self):
        for trigger in ('deadline', 'interrupt', 'death', 'wait-failure'):
            with self.subTest(trigger=trigger):
                api, clock = Fake(), Clock()
                dog = m.WatchdogControl(api, 31, 10, 32, 1, clock)
                self.assertIsNone(dog.step())
                if trigger == 'deadline': clock.now = 1
                if trigger == 'death': api.exited.add(32)
                if trigger == 'wait-failure': api.fail['wait'] = OSError('unknown')
                result = dog.step(interrupted=trigger == 'interrupt')
                self.assertFalse(result['cleanup_verified'])
                self.assertIn(('terminate_job', (31,)), api.calls)
                self.assertIn(('terminate_process', (10,)), api.calls)
                self.assertIsNone(dog.step())
                dog.close(); dog.close()
                self.assertCountEqual([a[0] for n, a in api.calls if n == 'close'], [31, 10, 32])

    def test_watchdog_failure_is_not_cleanup(self):
        self.api.fail['terminate_job'] = OSError('failed')
        dog = m.WatchdogControl(self.api, 31, 10, 32, 0, self.clock)
        self.assertEqual(len(dog.step()['errors']), 1)
        self.assertIn(('terminate_process', (10,)), self.api.calls)

    def test_sink_failure_cannot_lose_open_handle_or_prevent_close(self):
        def sink(row):
            if row.get('phase') == 'end' and row['api'] == 'open':
                raise OSError('disk failure')
        self.monitor.emit = sink
        with self.assertRaises(OSError): self.monitor.sample()
        self.assertIn(10, self.monitor.process_handles)
        self.monitor.close()
        self.assertIn(('close', (10,)), self.api.calls)

    def test_query_completion_past_cleanup_deadline(self):
        self.adopt()
        original = self.api.accounting
        def late(job):
            self.clock.now = 2
            return original(job)
        self.api.accounting = late
        self.assertFalse(self.cleanup()['complete'])

    def test_trace_corruption_and_unknown_never_replay_as_success(self):
        self.adopt()
        self.monitor.sample()
        self.cleanup()
        self.monitor.close()
        self.assertTrue(m.check_trace(self.rows))
        for kind in ('sample', 'cleanup', 'close'):
            damaged = [r for r in self.rows if r.get('kind') != kind]
            self.assertFalse(m.check_trace(damaged))
        damaged = copy.deepcopy(self.rows)
        damaged.pop(next(i for i, r in enumerate(damaged) if r.get('phase') == 'end'))
        self.assertFalse(m.check_trace(damaged))
        for field, value in [('complete', False), ('memory_bytes', None), ('error', 'denied')]:
            damaged = copy.deepcopy(self.rows)
            next(r for r in damaged if r.get('kind') == 'sample')[field] = value
            self.assertFalse(m.check_trace(damaged))
        damaged = copy.deepcopy(self.rows)
        next(r for r in damaged if r.get('kind') == 'cleanup')['waits'] = [False]
        self.assertFalse(m.check_trace(damaged))

    def test_mock_ctypes_adapter_layout_rights_and_exit259(self):
        # Calls are Python functions; no DLL is loaded and no Windows API executes.
        class Function:
            def __init__(self, fn): self.fn = fn
            def __call__(self, *args): return self.fn(*args)
        class DLL:
            def __init__(self): self.functions = {}
            def __getattr__(self, name):
                return self.functions.setdefault(name, Function(lambda *a: 1))
        dll = DLL()
        with patch('os.name', 'nt'), patch('ctypes.WinDLL', create=True, return_value=dll):
            api = m.WindowsAPI()
        dll.GetProcessId.fn = lambda h: 900
        def times(h, creation, *unused):
            m.C.cast(creation, m.C.POINTER(m.C.c_uint64))[0] = 0xfedcba9876543210
            return 1
        dll.GetProcessTimes.fn = times
        self.assertEqual(api.identity(10), (900, 0xfedcba9876543210))
        dll.OpenProcess.fn = lambda rights, inherit, pid: (self.assertEqual(rights, 0x101000),
            self.assertFalse(inherit), 77)[-1]
        self.assertEqual(api.open(900), 77)
        dll.WaitForSingleObject.fn = lambda h, ms: 258
        self.assertFalse(api.wait(10))
        dll.WaitForSingleObject.fn = lambda h, ms: 0
        self.assertTrue(api.wait(10))
        def exit_code(h, output):
            m.C.cast(output, m.C.POINTER(m.DWORD))[0] = 259
            return 1
        dll.GetExitCodeProcess.fn = exit_code
        self.assertEqual(api.exit_code(10), 259)
        def memory(h, output, size):
            self.assertEqual(size, m.C.sizeof(m.Memory))
            ptr = m.C.cast(output, m.C.POINTER(m.Memory))
            self.assertEqual(ptr.contents.cb, size)
            ptr.contents.ws = 4096
            return 1
        dll.K32GetProcessMemoryInfo.fn = memory
        self.assertEqual(api.memory(10), 4096)
        def overflow(job, kind, output, size, length):
            ptr = m.C.cast(output, m.C.POINTER(m.DWORD))
            ptr[0], ptr[1] = 257, 256
            return 1
        dll.QueryInformationJobObject.fn = overflow
        with self.assertRaises(m.Incomplete): api.members(1)
        dll.ResumeThread.fn = lambda h: 2
        with self.assertRaises(m.Incomplete): api.resume(11)


if __name__ == '__main__': unittest.main()
