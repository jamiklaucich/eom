import os
import sys
import time
import pyvisa as visa
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks, savgol_filter

def res_pow_calib(laser, pow_met, pows, wl_init=1550, wl_span=1, wl_step = 0.01,measure_wait=1 ):
    res_wls=np.zeros_like(pows)
    wl_c=wl_init
    wl_start = wl_c - wl_span/2; # start wavelength [nm]
    wl_end = wl_c + wl_span/2; # stop wavelength [nm]
    wls = np.linspace(wl_start, wl_end, int((wl_end-wl_start)/wl_step+1))
    sweep_pows = np.zeros_like(wls)
    laser.Write("SO")
    for i, pow, in enumerate(pows):
        laser.Write(f"LP{pow}")
        pow_met.read
        time.sleep(measure_wait)
        for j, wl in enumerate(wls):
            laser.Write("WA{}".format(wl))
            time.sleep(measure_wait)
            sweep_pows[j] = pow_met.read
        window_length = 5  # Choose an odd number
        polyorder = 2
        smoothed_data = savgol_filter(-sweep_pows, window_length, polyorder)
        peaks, _ = find_peaks(smoothed_data)
        peak_wl=wls[peaks[0]]
        res_wls[i]=peak_wl
        # plt.plot(wls,smoothed_data)
        # plt.plot(wls,-sweep_pows)
        # plt.show()
        wl_diff = peak_wl-wl_c
        wl_c+=wl_diff
        wls+=wl_diff#moves wls along so centre is at new peak
        print(f"{pow:.4f}mW \t{peak_wl:.4f}nm")
    laser.Write("SC")
    return res_wls
