import os
import csv
import math
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import numpy as np

def make_folder(folder_name):
    #makes a folder if it doesn't exist already
    os.makedirs(folder_name, exist_ok=True)

#text output
def write_vars(folder_name, **kwargs):
    make_folder(folder_name)
    file_path = os.path.join(folder_name, 'variables.txt')
    with open(file_path, "w") as f:
        for var_name, var_value in kwargs.items():
            f.write(f"{var_name}: {var_value}\n")

def write_xy(x,y, xhead, yhead, csvname):
    folder_name = os.path.dirname(csvname)
    if(folder_name):
        make_folder(folder_name)
    with open('{}.csv'.format(csvname), 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow([xhead, yhead])
        for x, y in zip(x, y):
            csvwriter.writerow([x, y])

def progress_bar(cur_val, max_val):
    bar = ["█" if j < int((20*(cur_val+1))/max_val) else "▁" for j in range(11)]
    string = "Progress:"+"".join(bar)+"{:.0f}%".format( (100*cur_val/max_val))

    return string

def progress_bar_time(cur_val, max_val, cur_time):
    bar = ["█" if j < int((20*(cur_val+1))/max_val) else "▁" for j in range(20)]
    progress = cur_val/max_val
    est_time = cur_time/progress
    time_left = est_time-cur_time
    string = "Progress:"+"".join(bar)+"{:.0f}% (~{:.0f}s left)".format( (100*progress), time_left)

    return string

#figure output
def line_plot(x,y,label=None, xlabel=None, ylabel=None, fig=None,ax=None, fname=None, xlim=None, ylim=None):
    #A basic line plot
    if(not fig and not ax):
        fig, ax = plt.subplots()
    ax.plot(x, y, label=label)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.axis("tight")
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    if(fname):
        os.makedirs(os.path.dirname(fname), exist_ok=True)
        fig.savefig(fname,dpi=300,bbox_inches='tight')
    plt.close()

    return fig, ax

def interpolate(x,y, x_new):
    #returns interpolated y values
    spline_y = interp1d(x, y, kind='cubic')
    #spline function
    y_new = spline_y(x_new)
    return y_new

def get_refractive(csv_path):
  #Retrieves wavelength, the refractive index, and if present the extinction coefficient
  data = []
  with open(csv_path, 'r') as f:
    reader = csv.reader(f)
    headers = next(reader)  # Read the first line (the headers)
    for row in reader:
      data.append(row)
  # Convert the data list to a dictionary, with the first column as the keys and the second column as the values
  k = np.array([0.0 for row in data])
  wav = np.array([float(row[0]) for row in data])
  n = np.array([float(row[1]) for row in data])
  if(len(data[0])>2):
    k = np.array([float(row[2]) for row in data])
  refr = np.array([n[i]+1.0j*k[i] for i in range(len(data))])

  return wav, refr

def split_array(arr, num_splits):
    #splits an array into parts as equal as possible.
    #useful for splitting data for multithreaded code
    # Calculate the length of each sub-array
    sub_length = len(arr) // num_splits
    # Calculate the number of leftover elements after the equal split
    remainder = len(arr) % num_splits
    # Create an empty list to store the sub-arrays
    sub_arrays = []
    # Split the array into sub-arrays of equal length
    for i in range(num_splits):
        start = i*sub_length + min(i, remainder)
        end = (i+1)*sub_length + min(i+1, remainder)
        sub_arrays.append(arr[start:end])
    # Return the list of sub-arrays
    return sub_arrays

def split_indicies(index, num_splits):
    indices = np.arange(index+1)
    splits = split_array(indices, num_splits)
    return splits