# coding: utf-8

"""
Default selection for m(ttbar).
"""

from operator import and_
from functools import reduce
from collections import defaultdict

from columnflow.util import maybe_import
from columnflow.production.util import attach_coffea_behavior

from columnflow.selection import Selector, SelectionResult, selector
from columnflow.selection.stats import increment_stats
from columnflow.selection.cms.met_filters import met_filters
from columnflow.selection.cms.json_filter import json_filter
from columnflow.production.categories import category_ids
from columnflow.production.cms.mc_weight import mc_weight
from columnflow.production.processes import process_ids
from mtt.selection.cutflow_features import cutflow_features

from mtt.selection.general import jet_energy_shifts
from mtt.selection.lepton import lepton_selection




np = maybe_import("numpy")
ak = maybe_import("awkward")


@selector(
    uses={
        lepton_selection,
        category_ids,
        process_ids, increment_stats, attach_coffea_behavior,
        mc_weight,
        met_filters,
        json_filter,
        cutflow_features,
        
    },
    produces={
        lepton_selection,
        category_ids,
        process_ids, increment_stats, attach_coffea_behavior,
        mc_weight,
        met_filters,
        json_filter,
        cutflow_features,
        
    },
    
    exposed=True,
)
def testing(
    self: Selector,
    events: ak.Array,
    stats: defaultdict,
    **kwargs,
) -> tuple[ak.Array, SelectionResult]:
    # ensure coffea behavior
    events = self[attach_coffea_behavior](events, **kwargs)

    # prepare the selection results that are updated at every step
    results = SelectionResult()

    # MET filters
    events, met_filters_results = self[met_filters](events, **kwargs)
    results.steps.METFilters = met_filters_results.steps.met_filter

    # JSON filter (data-only)
    if self.dataset_inst.is_data:
        events, json_filter_results = self[json_filter](events, **kwargs)
        results.steps.JSON = json_filter_results.steps.json

    # lepton selection
    events, lepton_results = self[lepton_selection](events, **kwargs)
    results += lepton_results

   
   

   
   
    # combined event selection after all steps
    event_sel = reduce(and_, results.steps.values())
    results.event = event_sel

    for step, sel in results.steps.items():
        n_sel = ak.sum(sel, axis=-1)
        print(f"{step}: {n_sel}")

    n_sel = ak.sum(event_sel, axis=-1)
    print(f"__all__: {n_sel}")

   
    # add cutflow features
    events = self[cutflow_features](events, results=results, **kwargs)

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



   
