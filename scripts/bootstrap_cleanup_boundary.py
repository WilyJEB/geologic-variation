"""Finite offline role model; no APIs, threads, transport or native entry point.

Models the vulnerable interval after the FIRST successful harness creation.
Readiness requires helper execution. No OS containment is assumed. Handles are
capabilities of their owning process, not autonomous cleanup agents.
"""
from dataclasses import dataclass, replace


@dataclass(frozen=True)
class State:
    first: str
    controller_alive: bool = True
    helper_scheduled: bool = False
    helper_alive: bool = True
    exact_creation_handles_owned: bool = True
    target_created: bool = False

    def cleanup_agents(self):
        return tuple(role for role, available in (
            ('controller', self.controller_alive and self.exact_creation_handles_owned),
            (self.first, self.helper_alive and self.helper_scheduled),
        ) if available)


def transitions(state):
    """Fake scheduler: permits controller death before first helper instruction."""
    if state.controller_alive:
        yield 'controller-death', replace(state, controller_alive=False,
                                           exact_creation_handles_owned=False)
    if state.helper_alive and not state.helper_scheduled:
        yield 'schedule-helper', replace(state, helper_scheduled=True)


def uncovered_prefixes(first):
    if first not in ('watchdog', 'sampler'):
        raise ValueError('only the two proposed helper roles')
    initial = State(first)
    pending = [(initial, ('create-first-helper-and-own-exact-handles',))]
    seen, failures = set(), []
    while pending:
        state, trace = pending.pop()
        if state in seen:
            continue
        seen.add(state)
        if state.helper_alive and not state.cleanup_agents():
            failures.append(dict(trace=list(trace), first=first,
                                 target_created=state.target_created,
                                 cleanup_agents=list(state.cleanup_agents())))
        pending.extend((next_state, trace + (event,))
                       for event, next_state in transitions(state))
    return failures
