"""Finite candidate-D contract simulator. No native API, transport or runner.

Each method is one abstract linearization point, not Python thread safety.
An issued pull pins its source until completion or receiver death. Seal does
not cancel an issued call: its successful return must still enter inventory.
"""

# Static nontransferable issuance cells, charged BEFORE the call, even on error.
CALLS = {
    'C': {'ordinary': {'poll_wait': 200, 'bootstrap_transfer_query': 700,
                       'evidence_io': 200},
          'cleanup': {'poll_wait': 400, 'terminate_query_close': 40, 'evidence_io': 8}},
    'W': {'ordinary': {'poll_wait': 200, 'bootstrap_transfer_query': 700,
                       'evidence_io': 200},
          'cleanup': {'poll_wait': 400, 'terminate_query_close': 40, 'evidence_io': 8}},
    'S': {'ordinary': {'sample_query_wait': 400, 'bootstrap_evidence_io': 200},
          'cleanup': {'quiesce_close': 32, 'evidence_io': 64}},
    'P': {'ordinary': {'create_handshake_exit': 136}, 'cleanup': {'close_exit': 16}},
    'T': {'ordinary': {'handshake_exit': 136}, 'cleanup': {'close_exit': 16}},
}
# Bytes issued to storage, including failed writes; no retry/reuse/borrowing.
# 8 MiB per row, six rows 48 MiB plus suite source/provenance 8 MiB = 56 MiB.
BYTES = {r: {'ordinary': n * 1024, 'cleanup': k * 1024}
         for r, n, k in [('C', 2048, 1024), ('W', 2048, 1024),
                         ('S', 1024, 512), ('P', 128, 128), ('T', 128, 128)]}


class Refused(Exception):
    pass


def charge(remaining, role, phase, category, amount):
    """Finite fake issuance check: no refund on failure, no adjacent-cell use."""
    cell = remaining[role][phase]
    if amount < 0 or category not in cell or cell[category] < amount:
        raise Refused('quota exhausted')
    cell[category] -= amount


class Stage:
    """One fixed epoch; symbolic handles are (role, label), never OS numbers."""
    def __init__(self):
        self.owners = {'C': {'H', 'J'}, 'W': set(), 'S': set()}
        self.alive = {'C', 'W', 'S'}
        self.members = {'H': {'W', 'S'}, 'J': set()}
        self.pending, self.done, self.acks = set(), set(), set()
        self.ready = False
        self.sealed = False
        self.users = set()
        self.closed = set()
        self.proven = set()
        self.helpers_proven = set()
        self.actions = []
        self.failed = False

    def issue(self, key):
        # Fixed typed transfer IDs for epoch 1. W pulls locally; no remote close.
        if (self.sealed or 'C' not in self.alive or 'W' not in self.alive
                or key not in ('J', 'Cwait', 'Swait', 'H', 'P', 'T')
                or key in self.pending | self.done
                or (key in ('P', 'T') and key not in self.members['J'])
                or (key == 'H' and not self.ready)):
            raise Refused('invalid issuance')
        self.pending.add(key)
        self.users.add(('W', key))

    def returned(self, key, success=True):
        if key not in self.pending or 'W' not in self.alive:
            raise Refused('no live issued receiver')
        # Mandatory first local action, even after seal. No ACK/sink dependency.
        if success:
            self.owners['W'].add(key)
        else:
            self.failed = True
        self.pending.remove(key)
        self.users.remove(('W', key))
        self.done.add(key)

    def establish_control(self, independent):
        if self.sealed or 'W' not in self.alive or not independent or not {'J', 'Cwait', 'Swait'} <= self.owners['W']:
            raise Refused('ACK is not independent control')
        self.ready = True

    def ack(self, epoch, role, key):
        if (self.sealed or epoch != 1 or role != 'W' or key in self.acks
                or key not in self.owners['W'] or key not in self.done):
            raise Refused('invalid ACK')
        self.acks.add(key)

    def target(self):
        if self.failed or self.sealed or self.members['J'] or not self.ready or 'H' not in self.acks or self.alive != {'C', 'W', 'S'}:
            raise Refused('target forbidden')
        self.members['J'] = {'P', 'T'}  # abstract maximum, atomically J-contained

    def death(self, role):
        self.alive.discard(role)
        self.owners[role].clear()  # only that process's copies close
        if role == 'W':
            self.pending.clear()
            self.users.clear()
        if not any('H' in self.owners[r] for r in self.alive):
            # Assumed eventual successful OS last-close containment, no evidence.
            for helper in ('W', 'S'):
                self.alive.discard(helper)
                self.owners[helper].clear()
            self.pending.clear()
            self.users.clear()

    def cleanup(self, role, *, empty, active, signaled):
        if role not in self.alive or 'J' not in self.owners[role]:
            raise Refused('no retained control')
        self.actions.append((role, 'terminate-J'))  # assumed call; no sink/peer use
        self.sealed = True
        if empty is True and active == 0 and self.members['J'] <= set(signaled):
            self.proven.add(role)
            return True
        self.failed = True
        return False

    def seal(self):
        self.sealed = True

    def helper_proof(self, role, *, exact_waits, empty, active):
        needed = {'W', 'S'} if role == 'C' else {'S'}
        if needed <= set(exact_waits) and empty is True and active == 0:
            self.helpers_proven.add(role)

    def close(self, role, key):
        if (not self.sealed or self.users or role not in self.proven
                or key not in self.owners[role] or (role, key) in self.closed):
            raise Refused('not quiescent/proven/local')
        if key == 'H' and (role not in self.helpers_proven or
                           (role == 'W' and self.owners['W'] != {'H'})):
            raise Refused('helpers unresolved or H not last')
        self.owners[role].remove(key)
        self.closed.add((role, key))  # consumed before attempted native close
        if role == 'W' and key == 'H' and 'C' not in self.alive:
            self.death('W')  # no post-self-termination record is manufactured
            self.actions.append(('external-model', 'W-self-evidence-unavailable'))


def armed():
    s = Stage()
    for key in ('J', 'Cwait', 'Swait'):
        s.issue(key)
        s.returned(key)
    s.establish_control(True)
    return s
