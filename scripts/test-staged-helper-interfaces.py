"""Offline distinguishing schedules, not concurrent/native execution tests."""
import unittest
import copy
from staged_helper_interfaces import Stage, Refused, armed, CALLS, BYTES, charge


class Tests(unittest.TestCase):
    def test_no_ack_or_partial_pull_can_arm(self):
        s = Stage()
        with self.assertRaises(Refused): s.issue('H')
        s.issue('J'); s.returned('J'); s.ack(1, 'W', 'J')
        with self.assertRaises(Refused): s.establish_control(True)
        with self.assertRaises(Refused): s.establish_control(False)
        with self.assertRaises(Refused): s.target()
        s.death('C')
        self.assertFalse(s.alive)

    def test_death_on_each_side_of_H_return(self):
        for point in ('before-issue', 'issued', 'returned', 'acked'):
            s = armed()
            if point != 'before-issue': s.issue('H')
            if point in ('returned', 'acked'): s.returned('H')
            if point == 'acked': s.ack(1, 'W', 'H')
            s.death('C')
            self.assertEqual('W' in s.alive, point in ('returned', 'acked'))
            if 'W' in s.alive:
                self.assertTrue(s.ready)
                self.assertTrue(s.cleanup('W', empty=True, active=0, signaled=[]))

    def test_lost_replayed_and_wrong_ACK(self):
        s = armed(); s.issue('H'); s.returned('H')
        self.assertIn('H', s.owners['W'])
        with self.assertRaises(Refused): s.target()
        for epoch, role in ((0, 'W'), (1, 'S')):
            with self.assertRaises(Refused): s.ack(epoch, role, 'H')
        s.ack(1, 'W', 'H'); s.target()
        with self.assertRaises(Refused): s.ack(1, 'W', 'H')
        with self.assertRaises(Refused): s.issue('H')
        self.assertFalse(s.owners['S'])

    def test_failed_acquisition_and_local_closes(self):
        s = armed(); s.issue('H'); s.returned('H', False)
        with self.assertRaises(Refused): s.ack(1, 'W', 'H')
        with self.assertRaises(Refused): s.target()
        s = armed(); s.issue('H'); s.returned('H'); s.seal()
        s.cleanup('C', empty=True, active=0, signaled=[])
        with self.assertRaises(Refused): s.close('C', 'H')
        s.helper_proof('C', exact_waits=['W', 'S'], empty=True, active=0)
        s.close('C', 'H')
        self.assertIn('H', s.owners['W'])
        with self.assertRaises(Refused): s.close('C', 'H')

    def test_seal_keeps_raced_success_and_unjoined_user(self):
        s = armed(); s.issue('H'); s.seal()
        s.cleanup('C', empty=True, active=0, signaled=[])
        with self.assertRaises(Refused): s.close('C', 'J')
        s.returned('H')
        self.assertIn('H', s.owners['W'])
        with self.assertRaises(Refused): s.ack(1, 'W', 'H')
        with self.assertRaises(Refused): s.issue('P')

    def test_survivor_cleanup_no_blocked_peer_or_sink_dependency(self):
        for survivor, dead in (('C', 'W'), ('W', 'C')):
            for dies in (False, True):
                s = armed(); s.issue('H'); s.returned('H'); s.ack(1, 'W', 'H'); s.target()
                if dies: s.death(dead)
                # Non-dead peer/S may remain blocked with copies. No method on them.
                self.assertFalse(copy.deepcopy(s).cleanup(survivor, empty=None, active=0, signaled=['P', 'T']))
                self.assertFalse(copy.deepcopy(s).cleanup(survivor, empty=True, active=0, signaled=['P']))
                self.assertTrue(s.cleanup(survivor, empty=True, active=0, signaled=['P', 'T']))
        s = armed(); s.issue('H'); s.returned('H'); s.death('S')
        for survivor in ('C', 'W'):
            self.assertTrue(s.cleanup(survivor, empty=True, active=0, signaled=[]))

    def test_W_self_containment_has_no_final_row(self):
        s = armed(); s.issue('H'); s.returned('H'); s.death('C'); s.seal()
        self.assertTrue(s.cleanup('W', empty=True, active=0, signaled=[]))
        s.helper_proof('W', exact_waits=['S'], empty=True, active=0)
        with self.assertRaises(Refused): s.close('W', 'H')
        s.close('W', 'J'); s.close('W', 'Cwait'); s.close('W', 'Swait')
        s.close('W', 'H')
        self.assertNotIn('W', s.alive)
        self.assertEqual(s.actions[-1], ('external-model', 'W-self-evidence-unavailable'))

    def test_static_disjoint_resource_cells(self):
        self.assertEqual(sum(sum(v['ordinary'].values()) for v in CALLS.values()), 3072)
        self.assertEqual(sum(sum(v['cleanup'].values()) for v in CALLS.values()), 1024)
        per_case = sum(sum(v.values()) for v in BYTES.values())
        self.assertEqual(per_case, 8 * 1024**2)
        self.assertLessEqual(per_case * 6 + 8 * 1024**2, 128 * 1024**2)
        for role in ('C', 'W'):
            self.assertEqual(CALLS[role]['ordinary']['poll_wait'], 2 * 100)
            self.assertEqual(CALLS[role]['cleanup']['poll_wait'], 2 * 200)
        remaining = copy.deepcopy(CALLS)
        charge(remaining, 'C', 'ordinary', 'bootstrap_transfer_query', 700)
        # A failed acquisition has no refund; W/cleanup capacity cannot be borrowed.
        with self.assertRaises(Refused):
            charge(remaining, 'C', 'ordinary', 'bootstrap_transfer_query', 1)
        self.assertEqual(remaining['W'], CALLS['W'])
        self.assertEqual(remaining['C']['cleanup'], CALLS['C']['cleanup'])


if __name__ == '__main__': unittest.main()
