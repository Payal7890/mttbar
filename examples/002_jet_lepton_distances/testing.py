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

def plot_two_variables_on_same_canvas(binning1, data1, binning2, data2, xlabel1, xlabel2, plot_label):
    """
    A function to plot two datasets on the same canvas.

    Parameters:
    binning1 (np.array): Binning for the first dataset.
    data1 (np.array): Data for the first dataset.
    binning2 (np.array): Binning for the second dataset.
    data2 (np.array): Data for the second dataset.
    xlabel1 (str): Label for the x-axis of the first dataset.
    xlabel2 (str): Label for the x-axis of the second dataset.
    plot_label (str): Label for the plot.

    Returns:
    None
    """
    
    fig, ax = plt.subplots()
    
    # Plot the first variable
    hist_last1 = data1[-1]
    data1 = np.append(data1, hist_last1)
    ax.step(binning1, data1, where='mid', label=f'{xlabel1} (Variable 1)')
    
    # Plot the second variable
    hist_last2 = data2[-1]
    data2 = np.append(data2, hist_last2)
    ax.step(binning2, data2, where='mid', label=f'{xlabel2} (Variable 2)', linestyle='--')
    
    ax.set_xlabel('Variable')
    ax.legend()
    #plt.savefig(f"tests/{plot_label}.png")

# Example usage for plotting two variables on the same canvas

# For the first variable
pickle_file_paths_1 = [
    '/nfs/dust/cms/user/payalroy/mttbar/data/mtt_store/analysis_mtt/cf.MergeHistograms/run2_2017_nano_v9_limited/tt_dl_powheg/nominal/calib__skip_jecunc/sel__dummy/prod__weights/weight__all_weights/v13/hist__electron_pt.pickle'
]

binning1, accumulated_data1 = load_and_accumulate_data_from_paths(
    pickle_file_paths_1,
    'muon_pt',
    [0, 1111]
)

# For the second variable
pickle_file_paths_2 = [
    '/nfs/dust/cms/user/payalroy/mttbar/data/mtt_store/analysis_mtt/cf.MergeHistograms/run2_2017_nano_v9_limited/tt_dl_powheg/nominal/calib__skip_jecunc/sel__dummy/prod__weights/weight__all_weights/v13/hist__vetoelectron_pt.pickle'
]

binning2, accumulated_data2 = load_and_accumulate_data_from_paths(
    pickle_file_paths_2,
    'vetomuon_pt',
    [0, 1111]
)

plot_two_variables_on_same_canvas(
    binning1, accumulated_data1,
    binning2, accumulated_data2,
    'Electron pt', 'VetoElectron pt',
    'combined_plot'
)

plt.savefig("pT.png")