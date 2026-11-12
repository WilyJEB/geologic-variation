"""Fake role/scheduler tests only; no native imports or process experiments."""
import unittest
from dataclasses import replace
from bootstrap_cleanup_boundary import State, transitions, uncovered_prefixes


class Tests(unittest.TestCase):
    def test_both_creation_orders_have_uncovered_prefix(self):
        for role in ('watchdog', 'sampler'):
            failures = uncovered_prefixes(role)
            self.assertEqual(len(failures), 1)
            self.assertEqual(failures[0]['trace'], [
                'create-first-helper-and-own-exact-handles', 'controller-death'])
            self.assertEqual(failures[0]['cleanup_agents'], [])
            self.assertFalse(failures[0]['target_created'])

    def test_live_controller_can_cleanup_exact_first_helper(self):
        self.assertEqual(State('watchdog').cleanup_agents(), ('controller',))

    def test_scheduled_helper_is_only_a_candidate_not_cleanup_proof(self):
        state = State('watchdog', controller_alive=False, helper_scheduled=True,
                      exact_creation_handles_owned=False)
        self.assertEqual(state.cleanup_agents(), ('watchdog',))
        # Availability does not assert successful termination, waits or evidence.

    def test_no_execution_is_required_before_controller_death(self):
        choices = dict(transitions(State('sampler')))
        self.assertFalse(choices['controller-death'].helper_scheduled)
        self.assertFalse(choices['controller-death'].exact_creation_handles_owned)
        self.assertTrue(choices['schedule-helper'].controller_alive)

    def test_no_unknown_supervisor_or_target_is_smuggled_into_model(self):
        with self.assertRaises(ValueError): uncovered_prefixes('supervisor')
        for state in (State('watchdog'), replace(State('sampler'), controller_alive=False)):
            self.assertFalse(state.target_created)
            self.assertTrue(set(state.cleanup_agents()) <= {'controller', 'watchdog', 'sampler'})


if __name__ == '__main__':
    unittest.main()
