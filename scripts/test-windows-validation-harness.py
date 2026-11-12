"""Mock-only harness tests. No native imports, transport or process execution."""
import ctypes as C
import importlib.util
import io
import copy
from pathlib import Path
import unittest
from unittest.mock import patch

with patch('ctypes.WinDLL', create=True, side_effect=AssertionError('DLL forbidden')):
    spec = importlib.util.spec_from_file_location('harness', Path(__file__).with_name('windows_validation_harness.py'))
    h = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(h)


class API:
    def __init__(self):
        self.calls, self.fail, self.exited = [], {}, set()
        self.pids, self.active, self.member_value = [], 0, True

    def call(self, op, *args):
        self.calls.append((op, args))
        if op in self.fail:
            raise self.fail[op]

    def atomic(self, job, argv, acquire):
        self.call('atomic', job, argv)
        acquire(10, 11)
    def identity(self, p): self.call('identity', p); return (100, 123456789012345678)
    def member(self, p, j): self.call('member', p, j); return self.member_value
    def path(self, p): self.call('path', p); return 'benign.exe'
    def resume(self, t): self.call('resume', t)
    def terminate_job(self, j): self.call('terminate_job', j)
    def wait(self, p): self.call('wait', p); return p in self.exited
    def close(self, p): self.call('close', p)
    def members(self, j): self.call('members', j); return self.pids
    def accounting(self, j): self.call('accounting', j); return dict(active=self.active)


class Transport:
    def __init__(self, dog):
        self.dog, self.fail, self.dead, self.calls = dog, None, False, []

    def pull(self, label, rights, acquire):
        self.calls.append((label, rights))
        if self.fail == label:
            raise OSError('duplicate failure')
        acquire(dict(job=31, peer=32, parent=33, sampler=34)[label])
        if self.fail == label + '-ack':
            raise OSError('lost ACK after acquisition')

    def arm_watchdog(self): return self.dog.arm(self.pull)
    def parent_to_watchdog(self, p): return self.dog.parent(self.pull)
    def watchdog_dead(self): return self.dead


class Tests(unittest.TestCase):
    def setUp(self):
        self.now = 0
        self.clock = lambda: self.now
        self.api = API()
        self.dog = h.Control(self.api, self.clock, 5)
        self.transport = Transport(self.dog)
        self.owner = h.Owner(self.api)
        self.owner.acquire('job', 1)
        self.wiring = h.Wiring(self.api, self.transport, self.owner, 1, self.clock, 2)

    def test_arm_before_atomic_and_parent_before_resume(self):
        original = self.api.atomic
        def atomic(*args):
            self.assertTrue(self.dog.armed)
            return original(*args)
        self.api.atomic = atomic
        original_resume = self.api.resume
        def resume(t):
            self.assertEqual(self.dog.owner.handles['parent'], 33)
            original_resume(t)
        self.api.resume = resume
        result = self.wiring.start(['benign.exe', 'N1'])
        self.assertEqual(result['identity'], (100, 123456789012345678))
        self.assertEqual(self.transport.calls, [('job', h.JOB_CONTROL), ('peer', h.SYNC), ('sampler', h.SYNC), ('parent', h.PARENT_CONTROL)])
        self.assertFalse(any(op == 'assign' for op, _ in self.api.calls))

    def test_each_transfer_failure_including_lost_ack(self):
        for point in ('job', 'peer', 'sampler', 'parent', 'job-ack', 'peer-ack', 'sampler-ack', 'parent-ack'):
            with self.subTest(point=point):
                self.setUp()
                self.transport.fail = point
                with self.assertRaises(OSError): self.wiring.start(['benign.exe'])
                self.assertFalse(self.wiring.ready)
                self.assertNotIn(('resume', (11,)), self.api.calls)
                self.assertIn(('terminate_job', (1,)), self.api.calls)
                expected = list(self.owner.handles.values()) + list(self.dog.owner.handles.values())
                self.owner.close(); self.dog.owner.close()
                self.owner.close(); self.dog.owner.close()
                self.assertCountEqual([args[0] for op, args in self.api.calls if op == 'close'], expected)

    def test_missing_readiness_ack_prevents_creation(self):
        self.transport.arm_watchdog = lambda: None
        with self.assertRaises(h.Invalid): self.wiring.start(['benign.exe'])
        self.assertFalse(any(op == 'atomic' for op, _ in self.api.calls))

    def test_ready_expired_or_watchdog_dead_prevents_creation(self):
        for dead in (False, True):
            self.setUp()
            self.transport.dead = dead
            if not dead: self.now = 2
            with self.assertRaises(h.Invalid): self.wiring.start(['benign.exe'])
            self.assertFalse(any(op == 'atomic' for op, _ in self.api.calls))

    def test_death_or_timeout_after_parent_transfer_never_resumes(self):
        for dead in (False, True):
            self.setUp()
            original = self.transport.parent_to_watchdog
            def transfer(p):
                result = original(p)
                if dead: self.transport.dead = True
                else: self.now = 2
                return result
            self.transport.parent_to_watchdog = transfer
            with self.assertRaises(h.Invalid): self.wiring.start(['benign.exe'])
            self.assertNotIn(('resume', (11,)), self.api.calls)
            self.assertIn('parent', self.owner.handles)

    def test_api_faults_and_interruptions_preserve_owned_handles(self):
        for op in ('atomic', 'identity', 'member', 'path', 'resume'):
            for error in (OSError('API failure'), KeyboardInterrupt()):
                self.setUp()
                self.api.fail[op] = error
                with self.assertRaises(type(error)): self.wiring.start(['benign.exe'])
                self.assertIn(('terminate_job', (1,)), self.api.calls)
                if op != 'atomic': self.assertEqual(self.owner.handles['parent'], 10)
                self.owner.close(); self.dog.owner.close()
                with self.assertRaises(h.Invalid): self.wiring.start(['benign.exe'])

    def test_false_atomic_membership_fails(self):
        self.api.member_value = False
        with self.assertRaises(h.Invalid): self.wiring.start(['benign.exe'])
        self.assertNotIn(('resume', (11,)), self.api.calls)

    def test_watchdog_fires_during_parent_transfer_keeps_receiver_ownership(self):
        original = self.transport.pull
        def pull(label, rights, acquire):
            original(label, rights, acquire)
            if label == 'parent': self.dog.step(interrupted=True)
        self.transport.pull = pull
        with self.assertRaises(h.Invalid): self.wiring.start(['benign.exe'])
        self.assertEqual(self.dog.owner.handles['parent'], 33)
        self.assertNotIn(('resume', (11,)), self.api.calls)
        self.dog.owner.close()
        self.assertIn(('close', (33,)), self.api.calls)

    def test_controller_death_before_parent_handoff(self):
        self.dog.arm(self.transport.pull)
        self.api.exited.add(32)
        result = self.dog.step()
        self.assertEqual(result['reason'], 'peer-death')
        self.assertIn(('terminate_job', (31,)), self.api.calls)
        self.assertFalse(result['cleanup_verified'])
        with self.assertRaises(h.Invalid): self.dog.parent(self.transport.pull)

    def test_watchdog_death_uses_independent_controller_role(self):
        # Symmetric role: peer is exact watchdog duplicate, job is controller copy.
        controller = h.Control(self.api, self.clock, 5)
        controller.arm(self.transport.pull)
        self.api.exited.add(32)
        self.assertEqual(controller.step()['reason'], 'peer-death')
        self.assertIn(('terminate_job', (31,)), self.api.calls)

    def test_sampler_death_without_controller_or_transport_response(self):
        self.dog.arm(self.transport.pull)
        self.api.exited.add(34)
        self.assertEqual(self.dog.step()['reason'], 'sampler-death')
        self.assertIn(('terminate_job', (31,)), self.api.calls)

    def test_blocked_sampler_and_sink_are_not_control_dependencies(self):
        class Blocked:
            def __getattribute__(self, name): raise AssertionError('sampler/sink touched')
        sampler, sink = Blocked(), Blocked()
        self.dog.arm(self.transport.pull)
        self.now = 5
        self.assertEqual(self.dog.step()['reason'], 'deadline')
        self.assertIsNone(self.dog.step())
        self.assertIsNotNone(sampler); self.assertIsNotNone(sink)

    def test_control_interrupt_wait_and_termination_failures(self):
        for op in ('interrupt', 'wait', 'terminate_job'):
            self.setUp()
            self.dog.arm(self.transport.pull)
            if op != 'interrupt': self.api.fail[op] = OSError(op)
            result = self.dog.step(interrupted=op != 'wait')
            self.assertFalse(result['cleanup_verified'])
            self.assertIn(('terminate_job', (31,)), self.api.calls)
            if op == 'terminate_job': self.assertTrue(result['errors'])

    def test_close_once_even_interrupted_or_failed(self):
        self.api.fail['close'] = KeyboardInterrupt()
        self.assertTrue(self.owner.close())
        self.assertEqual(self.owner.close(), [])
        self.assertEqual(self.api.calls, [('close', (1,))])

    def test_cleanup_requires_all_known_waits_and_both_job_queries(self):
        self.api.exited.update((10, 12))
        def verify(): return h.verify_cleanup(self.api, 1, [10, 12], self.clock, 10)
        self.assertTrue(verify()['complete'])
        self.api.exited.remove(12)
        self.assertFalse(verify()['complete'])
        self.api.exited.add(12)
        self.api.active = 1
        self.assertFalse(verify()['complete'])
        self.api.active = 0
        self.api.pids = [123]
        self.assertFalse(verify()['complete'])
        self.api.pids = []
        for op in ('members', 'accounting', 'wait'):
            self.api.fail = {op: OSError('unknown')}
            self.assertFalse(verify()['complete'])

    def test_late_cleanup_and_interrupted_cleanup_are_incomplete(self):
        original = self.api.accounting
        def late(j): self.now = 10; return original(j)
        self.api.accounting = late
        self.assertFalse(h.verify_cleanup(self.api, 1, [], self.clock, 10)['complete'])
        self.now = 0
        self.api.fail['members'] = KeyboardInterrupt()
        self.assertFalse(h.verify_cleanup(self.api, 1, [], self.clock, 10)['complete'])

    def test_durable_partial_rows_and_sticky_failure(self):
        stream, calls = io.StringIO(), []
        def sync():
            calls.append('sync')
            if len(calls) == 2: raise OSError('disk failure')
        writer = h.DurableRows(stream, sync)
        writer.append(dict(kind='api-start', complete=False))
        with self.assertRaises(OSError): writer.append(dict(kind='api-end', complete=False))
        partial = stream.getvalue()
        with self.assertRaises(h.Invalid): writer.append(dict(complete=True))
        self.assertEqual(stream.getvalue(), partial)
        self.assertIn('api-start', partial)
        self.owner.close()
        self.assertIn(('close', (1,)), self.api.calls)

    def test_truncated_write_preserved(self):
        class Partial(io.StringIO):
            def write(self, value):
                super().write(value[:8])
                raise OSError('partial write')
        stream = Partial()
        writer = h.DurableRows(stream, lambda: None)
        with self.assertRaises(OSError): writer.append(dict(kind='incomplete'))
        self.assertEqual(len(stream.getvalue()), 8)
        self.assertTrue(writer.failed)

    def test_incomplete_and_corrupted_evidence_rejected(self):
        rows = [dict(kind='case-start'),
                dict(kind='api-start', role='controller', sequence=0, api='members', monotonic=0),
                dict(kind='api-end', role='controller', sequence=0, api='members', monotonic=1),
                dict(kind='cleanup', complete=True, members=[], accounting=dict(active=0),
                     errors=[], waits=[dict(handle=10, signaled=True)], monotonic=2, deadline=3),
                dict(kind='case-end', complete=True)]
        self.assertTrue(h.check_evidence(rows, [10]))
        for index in range(len(rows)):
            self.assertFalse(h.check_evidence(rows[:index] + rows[index + 1:], [10]))
        for field, value in [('members', None), ('accounting', dict(active=1)),
                             ('waits', []), ('errors', ['unknown']), ('monotonic', 3)]:
            damaged = copy.deepcopy(rows)
            damaged[3][field] = value
            self.assertFalse(h.check_evidence(damaged, [10]))
        damaged = copy.deepcopy(rows)
        damaged[2]['error'] = 'denied'
        self.assertFalse(h.check_evidence(damaged, [10]))
        self.assertFalse(h.check_evidence(rows, [10, 11]))

    def test_short_write_and_flush_failure_are_sticky(self):
        for failure in ('short', 'flush'):
            class Stream(io.StringIO):
                def write(self, value):
                    if failure == 'short':
                        return super().write(value[:3])
                    return super().write(value)
                def flush(self):
                    if failure == 'flush': raise OSError('flush failed')
                    return super().flush()
            stream = Stream()
            writer = h.DurableRows(stream, lambda: None)
            with self.assertRaises((h.Invalid, OSError)): writer.append(dict(kind='incomplete'))
            self.assertTrue(writer.failed)
            before = stream.getvalue()
            with self.assertRaises(h.Invalid): writer.append(dict(kind='case-end', complete=True))
            self.assertEqual(before, stream.getvalue())

    def test_mock_creation_bindings_and_exact_flags_rights(self):
        class Function:
            def __init__(self, fn): self.fn = fn
            def __call__(self, *args): return self.fn(*args)
        class Kernel:
            def __init__(self): self.calls = []; self.fail = None
            def __getattr__(self, name):
                def invoke(*args):
                    self.calls.append(name)
                    if self.fail == name: return 0
                    if name == 'InitializeProcThreadAttributeList':
                        C.cast(args[3], C.POINTER(C.c_size_t))[0] = 128
                        return int(args[0] is not None)
                    if name == 'UpdateProcThreadAttribute':
                        self_test.assertEqual(args[2], 0x2000d)
                        self_test.assertEqual(C.cast(args[3], C.POINTER(C.c_void_p))[0], 1)
                    if name == 'CreateProcessW':
                        self_test.assertFalse(args[4])
                        self_test.assertEqual(args[5], 0x80004)
                        si = C.cast(args[8], C.POINTER(h.StartupEx))[0]
                        self_test.assertEqual(si.startup.cb, C.sizeof(h.StartupEx))
                        pi = C.cast(args[9], C.POINTER(h.ProcessInfo))[0]
                        pi.process, pi.thread = 10, 11
                    if name == 'DuplicateHandle':
                        self_test.assertEqual(args[4:], (h.PARENT_CONTROL, False, 0))
                        C.cast(args[3], C.POINTER(C.c_void_p))[0] = 33
                    return 1
                fn = Function(invoke)
                setattr(self, name, fn)
                return fn
        self_test = self
        k = Kernel()
        def require(ok):
            if not ok: raise OSError('fake WinError')
        bindings = h.CreationBindings(k, require, lambda: 122)
        acquired = []
        bindings.atomic(1, 'benign.exe', 'benign.exe N1', 'case', lambda p, t: acquired.extend([p, t]))
        self.assertEqual(acquired, [10, 11])
        self.assertEqual(k.calls[-1], 'DeleteProcThreadAttributeList')
        received = []
        bindings.pull(50, 10, 60, h.PARENT_CONTROL, received.append)
        self.assertEqual(received, [33])
        for failure in ('UpdateProcThreadAttribute', 'CreateProcessW', 'DuplicateHandle'):
            k.fail = failure
            acquired.clear(); received.clear()
            with self.assertRaises(OSError):
                if failure == 'DuplicateHandle': bindings.pull(50, 10, 60, h.PARENT_CONTROL, received.append)
                else: bindings.atomic(1, 'benign.exe', 'benign.exe', 'case', lambda *a: acquired.extend(a))
            self.assertEqual(acquired + received, [])
        self.assertEqual(C.sizeof(h.ProcessInfo), 2 * C.sizeof(C.c_void_p) + 8)


if __name__ == '__main__':
    unittest.main()
