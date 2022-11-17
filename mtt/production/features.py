# coding: utf-8

"""
Column production methods related to higher-level features.
"""

from columnflow.production import Producer, producer
from columnflow.production.categories import category_ids
from columnflow.production.mc_weight import mc_weight
from columnflow.util import maybe_import
from columnflow.columnar_util import EMPTY_FLOAT, Route, set_ak_column

ak = maybe_import("awkward")


@producer
def jet_energy_shifts(self: Producer, events: ak.Array, **kwargs) -> ak.Array:
    """
    Pseudo-producer that registers jet energy shifts.
    """
    return events


@jet_energy_shifts.init
def jet_energy_shifts_init(self: Producer) -> None:
    """
    Register shifts.
    """
    self.shifts |= {
        f"jec_{junc_name}_{junc_dir}"
        for junc_name in self.config_inst.x.jec.uncertainty_sources
        for junc_dir in ("up", "down")
    } | {"jer_up", "jer_down"}


@producer(
    uses={
        "Muon.pt", "Jet.pt", "BJet.pt",
    },
    produces={
        "ht_ak4",
        "n_jet_ak4",
        "ht_ak8",
        "n_jet_ak8",
        "n_muon",
    },
    shifts={
        jet_energy_shifts,
    },
)
def features(self: Producer, events: ak.Array, **kwargs) -> ak.Array:
    """High-level featues, e.g. scalar jet pt sum (ht), number of jets, electrons, muons, etc."""

    events = set_ak_column(events, "n_jet", ak.num(events.Jet.pt, axis=1))
    events = set_ak_column(events, "n_electron", ak.num(events.Electron.pt, axis=1))
    events = set_ak_column(events, "n_muon", ak.num(events.Muon.pt, axis=1))

    events = set_ak_column(events, "ht", ak.sum(events.Jet.pt, axis=1))

    return events


@producer(
    uses={
        mc_weight, category_ids,
        "Jet.pt", "FatJet.pt",
    },
    produces={
        mc_weight, category_ids,
        "cutflow.n_jet_ak4", "cutflow.ht_ak4",
        "cutflow.jet_ak4_1_pt", "cutflow.jet_ak4_2_pt", "cutflow.jet_ak4_3_pt", "cutflow.jet_ak4_4_pt",
        "cutflow.n_jet_ak8", "cutflow.ht_ak8",
        "cutflow.jet_ak8_1_pt", "cutflow.jet_ak8_2_pt", "cutflow.jet_ak8_3_pt", "cutflow.jet_ak8_4_pt",
    },
)
def cutflow_features(self: Producer, events: ak.Array, **kwargs) -> ak.Array:
    """High-level featues for cutflow."""
    events = self[mc_weight](events, **kwargs)
    events = self[category_ids](events, **kwargs)

    events = set_ak_column(events, "cutflow.n_jet_ak4", ak.num(events.Jet, axis=1))
    events = set_ak_column(events, "cutflow.n_jet_ak8", ak.num(events.FatJet, axis=1))

    events = set_ak_column(events, "cutflow.ht_ak4", ak.sum(events.Jet.pt, axis=1))
    events = set_ak_column(events, "cutflow.ht_ak8", ak.sum(events.FatJet.pt, axis=1))

    events = set_ak_column(events, "cutflow.jet_ak4_1_pt", Route("Jet.pt[:,0]").apply(events, EMPTY_FLOAT))
    events = set_ak_column(events, "cutflow.jet_ak4_2_pt", Route("Jet.pt[:,1]").apply(events, EMPTY_FLOAT))
    events = set_ak_column(events, "cutflow.jet_ak4_3_pt", Route("Jet.pt[:,2]").apply(events, EMPTY_FLOAT))
    events = set_ak_column(events, "cutflow.jet_ak4_4_pt", Route("Jet.pt[:,3]").apply(events, EMPTY_FLOAT))

    events = set_ak_column(events, "cutflow.jet_ak8_1_pt", Route("FatJet.pt[:,0]").apply(events, EMPTY_FLOAT))
    events = set_ak_column(events, "cutflow.jet_ak8_2_pt", Route("FatJet.pt[:,1]").apply(events, EMPTY_FLOAT))
    events = set_ak_column(events, "cutflow.jet_ak8_3_pt", Route("FatJet.pt[:,2]").apply(events, EMPTY_FLOAT))
    events = set_ak_column(events, "cutflow.jet_ak8_4_pt", Route("FatJet.pt[:,3]").apply(events, EMPTY_FLOAT))

    return events