"""Offline, instance-owned exact retained-site selection; no UI or player state.

Load only the existing card model's definitions and pinned archive reader.
Never invoke its renderer, builder or main entry point. Coordinates are native
retained x/z integers, not screen coordinates or Minecraft positions.
"""
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
import runpy


_CARD = runpy.run_path(str(Path(__file__).with_name('build-td-inspection-card.py')))


@dataclass(frozen=True)
class Selection:
    state: str
    coordinates: tuple | None = None
    site: object | None = None


class InspectionSelection:
    """One independent owner; construction validates the existing pinned inputs.

    select replaces the entire selection, even for unsupported/invalid input.
    reset clears both requested coordinates and the site. Snapshots are copies:
    callers cannot mutate the owner's retained history dictionaries or state.
    No selection is inferred on construction, reset, or an unsupported request.
    """

    def __init__(self):
        self.__data = _CARD['load']()
        self.__selection = Selection('empty')

    @property
    def selection(self):
        return deepcopy(self.__selection)

    def reset(self):
        self.__selection = Selection('empty')
        return self.selection

    def select(self, x, z):
        # Clear first so a lookup error cannot leave a stale supported card.
        self.__selection = Selection('invalid')
        if type(x) is not int or type(z) is not int:
            return self.selection
        coordinates = (x, z)
        site = _CARD['lookup'](x, z, self.__data)
        if site is not None:
            self.__selection = Selection('selected', coordinates, site)
        else:
            # Closed retained extent: lattice gaps inside, exterior outside.
            state = 'gap' if 2688 <= x <= 5760 and 10880 <= z <= 13952 else 'exterior'
            self.__selection = Selection(state, coordinates)
        return self.selection
