import os
import numpy as np
import hist
from hist import Hist
import matplotlib.pyplot as plt
import awkward as ak
import pickle

def check_paths(config, vers, dataset, task, calib, sel, prod, local_path):
    """
    A function to check if all paths exist
    and to give an array of existing paths.

    Parameters:
    config (str): configuration name e.g. 'run2_2017_nano_v9_limited'
    vers (str): version of the task e.g. 'v1'
    dataset (str): dataset name e.g. 'ttbar_dl_powheg'
    task (str): task name e.g. 'cf.MergeHistograms'
    local_path (str): path to the local directory e.g. '/nfs/dust/cms/use/matthiej/mttbar_MA/'

    Returns:
    existing_paths (np.array): array of existing paths
    """

    all_paths_exist = True
    existing_paths = np.array([])
    missing_paths = np.array([])
    print(dataset)
    for vs in np.array([vers]):
        for ts in np.array([task]):
            test_path = os.path.join(
                local_path,
                f"analysis_mtt/cf.{ts}/{config}/{dataset}/",
                f"nominal/calib__{calib}/sel__{sel}/prod__{prod}/{vs}/"
            )
            if not os.path.exists(test_path):
                all_paths_exist = False
                missing_paths = np.append(missing_paths, test_path)
                break
            existing_paths = np.append(existing_paths, test_path)
    print(f"All paths for {dataset} exist." if all_paths_exist else f"Some paths missing:{missing_paths}")
    return existing_paths


def cf_load_and_accumulate_data(ds_names, cf_var_name, config, cat_list, vers, task, calib, sel, prod, local_path):
    """
    A function to load and accumulate data from pickle files.

    Parameters:
    ds_names (list): list of dataset names, e.g. ['data_e_mu', 'ttbar_dl_powheg']
    cf_var_name (str): name of the variable, e.g. 'electron_eta'
    config (str): configuration name e.g. 'run2_2017_nano_v9_limited'
    cat_list (list): list of categories e.g. '[0, 1111, 2121]' (correspond to the catgeories in the histograms)
    vers (str): version of the task e.g. 'v1'
    task (str): task name e.g. 'cf.MergeHistograms'
    local_path (str): path to the local directory e.g. '/nfs/dust/cms/use/matthiej/mttbar_MA/'

    Returns:
    binning (np.array): binning of the data
    accumulated_data (np.array): accumulated data
    """

    output_paths = np.array([])
    for dataset_name in ds_names:
        output_paths = np.append(output_paths, check_paths(config, vers, dataset_name, task, calib, sel, prod, local_path))

    binning = None
    accumulated_data = None
    for category in cat_list:
        for output_path in output_paths:
            file_name = f'hist__{cf_var_name}.pickle'
            pickle_file = os.path.join(output_path, file_name)
            with open(pickle_file, 'rb') as f:
                data_hist = pickle.load(f)
                if binning is None:
                    binning = data_hist.axes[3].edges
                valid_categories = [entry for entry in data_hist.axes[0]]
                if category in valid_categories:
                    if accumulated_data is None:
                        accumulated_data = np.zeros(len(data_hist[hist.loc(category), 0, 0, :].values()))
                    accumulated_data += data_hist[hist.loc(category), 0, 0, :].values()
    return binning, accumulated_data


def plot_data(binning, data, xlabel, plot_label):
    """
    A function to plot data from histograms.
    
    Parameters:
    binning (np.array): binning of the data
    data (np.array): data to plot
    xlabel (str): x-axis label
    plot_label (str): label for the plot
    
    Returns:
    None
    """
    
    fig, ax = plt.subplots()
    hist_last = data[-1]
    data = np.append(data, hist_last)
    ax.step(binning, data, where='mid')
    ax.set_xlabel(xlabel)
   # plt.savefig(f"tests/{plot_label}.pdf")
    plt.savefig(f"tests/{plot_label}.png")


histogram_tt2_binning, histogram_tt2_data = cf_load_and_accumulate_data(
    ['tt_dl_powheg', 'tt_sl_powheg'],
    'electron_pt',
    'run2_2017_nano_v9_limited',
    [0, 1111],
    'v14',
    'MergeHistograms',
    'skip_jecunc',
    'default',
    'ttbar__features__weights',
    '/nfs/dust/cms/user/matthiej/mttbar_MA/data/mtt_store/'
    )


plot_data(histogram_tt2_binning, histogram_tt2_data, 'electron pt', 'step_plot2')
