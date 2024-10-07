# coding: utf-8

"""
Selectors to set ak columns for cutflow features
"""

from columnflow.util import maybe_import
from columnflow.columnar_util import set_ak_column, Route, EMPTY_FLOAT
from columnflow.selection import Selector, SelectionResult, selector

ak = maybe_import("awkward")


@selector(
    uses={
        "Muon.pt","Muon.eta",
    },
    produces={
        
        "cutflow.muon_pt", "cutflow.muon_eta",
        "cutflow.electron_pt", "cutflow.electron_eta",
      
        "cutflow.n_muon", "cutflow.n_electron",
    },
)
def cutflow_features(self: Selector, events: ak.Array, results: SelectionResult, **kwargs) -> ak.Array:

   

    # pt-leading electron/muon properties
    for lepton_name in ["Muon", "Electron"]:
        lepton_indices = results.objects[lepton_name][lepton_name]
        leptons = events[lepton_name][lepton_indices]
        for var in ("pt", "eta"):
            events = set_ak_column(
                events,
                f"cutflow.{lepton_name.lower()}_{var}",
                Route(f"{var}[:, 0]").apply(leptons, EMPTY_FLOAT),
            )

    # count number of objects after appyling selection
   
    events = set_ak_column(events, "cutflow.n_muon", ak.num(results.objects.Muon.Muon, axis=-1))
    events = set_ak_column(events, "cutflow.n_electron", ak.num(results.objects.Electron.Electron, axis=-1))

    if self.dataset_inst.is_mc and not self.dataset_inst.has_tag("is_diboson"):
        events = set_ak_column(events, "cutflow.lhe_ht", events.LHE.HT)

    return events


@cutflow_features.init
def cutflow_features_init(self: Selector) -> None:

    if (
        hasattr(self, "dataset_inst") and
        self.dataset_inst.is_mc and
        not self.dataset_inst.has_tag("is_diboson")
    ):
        self.uses |= {"LHE.HT"}
        self.produces |= {"cutflow.lhe_ht"}
