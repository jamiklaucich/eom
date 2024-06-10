import os
import sys
import time
import pyvisa as visa
import pandas as pd
import numpy as np
from scipy.signal import find_peaks

def res_pow_calib(laser, pow_met, pows, wl_init=1550, wl_span=1, wl_step = 0.01,measure_wait=1 ):
    res_wls=np.zeros_like(pows)
    wl_c=wl_init
    wl_start = wl_c - wl_span/2; # start wavelength [nm]
    wl_end = wl_c + wl_span/2; # stop wavelength [nm]
    wls = np.linspace(wl_start, wl_end, int((wl_end-wl_start)/wl_step+1))
    sweep_pows = np.zeros_like(wls)

    for i, pow, in enumerate(pows):
        laser.Write(f"LP{pow}")
        for j, wl in enumerate(wls):
            laser.Write("WA{}".format(wl))
            time.sleep(measure_wait)
            sweep_pows[j] = pow_met.read
        peaks, _ = find_peaks(sweep_pows)
        peak_wl=wls[peaks[0]]
        res_wls[i]=peak_wl
        wl_diff = peak_wl-wl_c
        wls+=wl_diff#moves wls along so centre is at new peak
        print(f"{pow:.4f}mW \t{peak_wl:.4f}nm")
    return res_wls
