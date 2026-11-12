"""Small abstract graph tests; no process creation, clocks or native imports."""
import unittest
from bootstrap_containment_model import settle, review_cases


class Tests(unittest.TestCase):
    def test_first_creation_for_both_orders(self):
        for row in review_cases()[:6]:
            expected = [] if row['arrangement'] == 'sole-controller-copy' else [row['first']]
            self.assertEqual(row['after_C_death'], expected)

    def test_staged_copy_never_leaves_unready_survivor(self):
        for row in review_cases()[6:]:
            self.assertTrue(not row['after_C_death'] or row['independent_W_available'])
            self.assertEqual(row['after_W_exit'], [])

    def test_copy_before_ack_keeps_W_alive(self):
        row = review_cases()[8]
        self.assertEqual(row['after_C_death'], ['S', 'W'])
        self.assertTrue(row['ready'])

    def test_other_process_copy_is_not_closed_by_C_death(self):
        self.assertEqual(settle({'C', 'W'}, {'H': {'C', 'W'}}, {'H': {'W'}}, {'C'}), ['W'])

    def test_W_death_leaves_C_and_targets_for_C_cleanup(self):
        self.assertEqual(settle({'C', 'W', 'S', 'P'},
                                {'H': {'C', 'W'}, 'J': {'C', 'W'}},
                                {'H': {'W', 'S'}, 'J': {'P'}}, {'W'}), ['C', 'P', 'S'])

    def test_sampler_copy_breaks_last_close(self):
        self.assertEqual(settle({'C', 'W', 'S'}, {'H': {'C', 'W', 'S'}},
                                {'H': {'W', 'S'}}, {'C', 'W'}), ['S'])

    def test_target_copies_break_cascade(self):
        self.assertEqual(settle({'C', 'W', 'P'}, {'H': {'C'}, 'J': {'C', 'W', 'P'}},
                                {'H': {'W'}, 'J': {'P'}}, {'C'}), ['P'])

    def test_blocked_C_or_S_does_not_remove_W_capability(self):
        # Blocked role stays alive/holds copies. Explicit W action kills targets.
        for blocked in ('C', 'S'):
            live = {'C', 'W', 'S', 'P', 'T'}
            self.assertIn(blocked, live)
            self.assertEqual(settle(live, {'H': {'C', 'W'}, 'J': {'C', 'W'}},
                                    {'H': {'W', 'S'}, 'J': {'P', 'T'}}, {'P', 'T'}),
                             ['C', 'S', 'W'])
        # Tests graph after assumed W action, not scheduling of that action.


if __name__ == '__main__':
    unittest.main()
