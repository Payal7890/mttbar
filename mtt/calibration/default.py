# coding: utf-8

"""
Calibration methods.
"""

from columnflow.calibration import Calibrator, calibrator
from columnflow.calibration.jets import jets
from columnflow.production.mc_weight import mc_weight
from columnflow.production.seeds import deterministic_seeds
from columnflow.util import maybe_import

from mtt.calibration.jets import jet_energy

ak = maybe_import("awkward")


@calibrator(
    uses={mc_weight, deterministic_seeds, jets},
    produces={mc_weight, deterministic_seeds, jets},
)
def default(self: Calibrator, events: ak.Array, **kwargs) -> ak.Array:
    if self.dataset_inst.is_mc:
        events = self[mc_weight](events, **kwargs)
    events = self[deterministic_seeds](events, **kwargs)
    events = self[jets](events, **kwargs)

    return events


@calibrator(
    uses={mc_weight, deterministic_seeds, jet_energy},
    produces={mc_weight, deterministic_seeds, jet_energy},
)
def skip_jecunc(self: Calibrator, events: ak.Array, **kwargs) -> ak.Array:
    """ only uses jec_nominal for test purposes """
    if self.dataset_inst.is_mc:
        events = self[mc_weight](events, **kwargs)
    events = self[deterministic_seeds](events, **kwargs)
    events = self[jet_energy](events, **kwargs)

    return events
