# coding: utf-8

"""
Script to plot variables after kinematic cuts.
"""
from collections import defaultdict

from columnflow.selection import Selector, SelectionResult, selector
from columnflow.selection.stats import increment_stats
from columnflow.selection.util import sorted_indices_from_mask
from columnflow.production.processes import process_ids
from columnflow.production.cms.mc_weight import mc_weight
from columnflow.util import maybe_import
from columnflow.production.categories import category_ids

#from mtt.selection.cutflow_features import cutflow_features



np = maybe_import("numpy")
ak = maybe_import("awkward")


#
# unexposed selectors
# (not selectable from the command line but used by other, exposed selectors)
#

@selector(
    uses={
        "Muon.pt", "Muon.eta",
        "Muon.highPtId", "Muon.tightId", "Muon.pfIsoId", "Muon.mediumId", "Muon.looseId",
        "Electron.pt", "Electron.eta", "Electron.deltaEtaSC", "Electron.cutBased",
        "HLT.IsoMu27",
        "HLT.Ele35_WPTight_Gsf",
        "Electron.mvaFall17V2Iso_WP80",
        "Electron.mvaFall17V2noIso_WP80",

    },
)
def my_selection(
    self: Selector,
    events: ak.Array,
    **kwargs,
) -> tuple[ak.Array, SelectionResult]:
   
   # muon_mask_lowpt = (abs(events.Muon.eta) < 2.4) & (events.Muon.pt > 30) & (events.Muon.pt < 55) & ((events.Muon.pfIsoId == 4) | (events.Muon.pfIsoId == 5) | (events.Muon.pfIsoId == 6)) & (events.Muon.tightId)
                    
    # filter valid muons by kinematics and ID (per-muon mask)
   # muon_mask_highpt = (events.Muon.pt > 55.0) & (abs(events.Muon.eta) < 2.4) & (events.Muon.highPtId == 2)

   # muon_mask = (muon_mask_lowpt | muon_mask_highpt)

   

    
    # filter valid electons by kinematics

    electron_mask_eta = (
        (abs(events.Electron.eta + events.Electron.deltaEtaSC) < 2.5) &
        # filter out electrons in barrel-endcap transition region
        ((abs(events.Electron.eta) < 1.44) | (abs(events.Electron.eta) > 1.57))
    )

    electron_mask_lowpt = (
        electron_mask_eta &
        (events.Electron.pt > 35) &
        (events.Electron.pt <= 120) &
        # MVA electron ID (WP 80, with isolation)
        (events.Electron.cutBased == 4)
    )
    electron_mask_highpt = (
        (events.Electron.pt > 120) &
         electron_mask_eta &
        (events.Electron.cutBased == 4)
    )

    electron_mask = (electron_mask_lowpt | electron_mask_highpt)
    electron_indices = sorted_indices_from_mask(electron_mask,events.Electron.pt)

   
    muon_mask_lowpt = (abs(events.Muon.eta) < 2.4) & (events.Muon.pt > 30) & (events.Muon.pt <= 55)   & (events.Muon.tightId)
    muon_mask_highpt = (abs(events.Muon.eta) < 2.4) & (events.Muon.pt > 55) & (events.Muon.tightId)


    muon_mask = (muon_mask_lowpt | muon_mask_highpt)
    muon_indices = sorted_indices_from_mask(muon_mask, events.Muon.pt)

    
    add_muons_lowpt = (events.Muon.pt > 15) & (abs(events.Muon.eta) < 2.4) & (events.Muon.tightId) & ~muon_mask_lowpt
    add_muons_highpt = (events.Muon.pt > 15) & (abs(events.Muon.eta) < 2.4) & (events.Muon.tightId) & ~muon_mask_highpt

    add_muons = add_muons_lowpt | add_muons_highpt
    add_muons_indices = sorted_indices_from_mask(add_muons, events.Muon.pt)

    add_electrons_lowpt = (events.Electron.pt > 15) &  (abs(events.Electron.eta + events.Electron.deltaEtaSC) < 2.5) & (events.Electron.cutBased == 4) & ~electron_mask_lowpt
    add_electrons_highpt =  (events.Electron.pt > 15) &  (abs(events.Electron.eta + events.Electron.deltaEtaSC) < 2.5) & (events.Electron.cutBased == 4) & ~electron_mask_highpt
    add_electrons = add_electrons_lowpt | add_electrons_highpt
    add_electrons_indices = sorted_indices_from_mask(add_electrons, events.Electron.pt)



    dummy = ak.ones_like(events.event, dtype=bool)

    # require the electron trigger to calculate efficiencies
    # NOTE: not needed here for baseline selection -> use categories
    # electron_trigger_sel = events.HLT.Ele35_WPTight_Gsf

    # build and return selection results
    # "objects" maps source columns to new columns and selections to be applied on the old columns
    # to create them, e.g. {"Muon": {"MySelectedMuon": indices_applied_to_Muon}}

    return events, SelectionResult(
        steps={
           "dummy": dummy
        },
        objects={
            "Muon": {
                "Muon": muon_indices,
                "VetoMuon": add_muons_indices
            },
            "Electron": {
                "Electron": electron_indices,
                "VetoElectron": add_electrons_indices
            },
        },
    )



# exposed selectors
# (those that can be invoked from the command line)
#

@selector(
    uses={
        # selectors / producers called within _this_ selector
        mc_weight, process_ids, my_selection, 
        category_ids,
        increment_stats,
    },
    produces={
        # selectors / producers whose newly created columns should be kept
        mc_weight, process_ids,
        category_ids,
    },
    exposed=True,
)
def dummy(
    self: Selector,
    events: ak.Array,
    stats: defaultdict,
    **kwargs,
) -> tuple[ak.Array, SelectionResult]:
    # prepare the selection results that are updated at every step
    results = SelectionResult()

    # my selection
    events, my_results = self[my_selection](events, **kwargs)
    results += my_results

   

    # combined event selection after all steps
    results.event = (
        results.steps.dummy 
        
       
    )

    

    # add cutflow features
   # events = self[cutflow_features](events, results=results, **kwargs)

    # build categories
    events = self[category_ids](events, results=results, **kwargs)

    # create process ids
    events = self[process_ids](events, **kwargs)

    # add mc weights (needed for cutflow plots)
    if self.dataset_inst.is_mc:
        events = self[mc_weight](events, **kwargs)

    # increment stats
    weight_map = {
        "num_events": Ellipsis,
        "num_events_selected": results.event,
    }
    group_map = {
        # per category
        "category": {
            "values": events.category_ids,
            "mask_fn": (lambda v: ak.any(events.category_ids == v, axis=1)),
        },
        # per step
        "step": {
            "values": list(results.steps),
            "mask_fn": (lambda v: results.steps[v]),
        },
    }
    if self.dataset_inst.is_mc:
        weight_map = {
            **weight_map,
            # mc weight for all events
            "sum_mc_weight": (events.mc_weight, Ellipsis),
            "sum_mc_weight_selected": (events.mc_weight, results.event),
        }
        group_map = {
            **group_map,
            # per process
            "process": {
                "values": events.process_id,
                "mask_fn": (lambda v: events.process_id == v),
            },
        }
    events, results = self[increment_stats](
        events,
        results,
        stats,
        weight_map=weight_map,
        group_map=group_map,
        **kwargs,
    )

    return events, results

