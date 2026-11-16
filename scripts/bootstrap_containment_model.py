"""Finite abstract handle graph. No OS, scheduling, transport or native bindings.

settle() is a semantic fixed point, NOT a time bound or measured termination.
"""


def settle(alive, holders, members, dead=()):
    alive = set(alive) - set(dead)
    while True:
        killed = set().union(*(set(members[j]) & alive
                               for j in holders if not (set(holders[j]) & alive)))
        if not killed:
            return sorted(alive)
        alive -= killed


def review_cases():
    rows = []
    for first in ('W', 'S'):
        for arrangement, copies, membership in (
                ('create-then-assign', {'H': {'C'}}, {'H': set()}),
                ('early-helper-copy', {'H': {'C', first}}, {'H': {first}}),
                ('sole-controller-copy', {'H': {'C'}}, {'H': {first}})):
            rows.append(dict(arrangement=arrangement, first=first,
                             after_C_death=settle({'C', first}, copies, membership, {'C'})))
    # W's independent control is established BEFORE it may acquire H.
    for phase, ready, copies, targets in (
            ('both-unready', False, {'C'}, set()),
            ('control-ready-before-copy', True, {'C'}, set()),
            ('copy-acquired-before-ack', True, {'C', 'W'}, set()),
            ('targets-created', True, {'C', 'W'}, {'P', 'T'})):
        live = {'C', 'W', 'S'} | targets
        holders = {'H': copies, 'J': {'C', 'W'}}
        members = {'H': {'W', 'S'}, 'J': targets}
        after = settle(live, holders, members, {'C'})
        # This is control availability, not proof that a native poll executes.
        available = ready and 'W' in after
        cleaned = settle(after, holders, {**members, 'J': set()}, targets) if available else after
        rows.append(dict(arrangement='staged-helper-copy', phase=phase,
                         ready=ready, H_owners=sorted(copies), after_C_death=after,
                         independent_W_available=available,
                         after_assumed_W_target_termination=cleaned,
                         after_W_exit=settle(cleaned, holders, members, {'W'})))
    return rows
