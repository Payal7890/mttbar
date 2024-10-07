import os
import numpy as np
import hist
from hist import Hist
import matplotlib.pyplot as plt
import pickle

def load_and_accumulate_data_from_paths(pickle_paths, cf_var_name, cat_list):
    """
    A function to load and accumulate data from given pickle file paths.

    Parameters:
    pickle_paths (list): List of full paths to pickle files.
    cf_var_name (str): Name of the variable, e.g. 'electron_pt'
    cat_list (list): List of categories e.g. '[0, 1111, 2121]'

    Returns:
    binning (np.array): Binning of the data.
    accumulated_data (np.array): Accumulated data.
    """
    
    binning = None
    accumulated_data = None
    
    for pickle_file in pickle_paths:
        with open(pickle_file, 'rb') as f:
            data_hist = pickle.load(f)
            
            if binning is None:
                binning = data_hist.axes[3].edges
                
            valid_categories = [entry for entry in data_hist.axes[0]]
            
            for category in cat_list:
                if category in valid_categories:
                    if accumulated_data is None:
                        accumulated_data = np.zeros(len(data_hist[hist.loc(category), 0, 0, :].values()))
                    
                    accumulated_data += data_hist[hist.loc(category), 0, 0, :].values()
    
    return binning, accumulated_data

def plot_data(binning, data, xlabel, plot_label):
    """
    A function to plot data from histograms.
    
    Parameters:
    binning (np.array): Binning of the data
    data (np.array): Data to plot
    xlabel (str): x-axis label
    plot_label (str): Label for the plot
    
    Returns:
    None
    """
    
    fig, ax = plt.subplots()
    hist_last = data[-1]
    data = np.append(data, hist_last)
    ax.step(binning, data, where='mid')
    ax.set_xlabel(xlabel)
    plt.savefig(f"tests/{plot_label}.png")

# Example usage
pickle_file_paths = [
    '/nfs/dust/cms/user/payalroy/mttbar/data/mtt_store/analysis_mtt/cf.MergeHistograms/run2_2017_nano_v9_limited/tt_dl_powheg/nominal/calib__skip_jecunc/sel__dummy/prod__weights/weight__all_weights/v4/hist__muon_pt.pickle'
    
]

binning, accumulated_data = load_and_accumulate_data_from_paths(
    pickle_file_paths,
    'muon_pt',
    [0, 1111]
)

plot_data(binning, accumulated_data, 'electron pt', 'step_plot2')
