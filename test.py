import os
import clr
import sys
import time
import pyvisa as visa
import numpy as np

wl_c = 1550#nm
wl_span = 1#nm
wl_step = 1;#step [nm]

v_start = 0#V
v_end = 2#V
v_step = 0.5#V

Optical_power = 1.0 #dBm

measure_wait = 0.025#s time between switching laser wvl and measuring pow

wl_start = wl_c - wl_span/2; # start wavelength [nm]
wl_end = wl_c + wl_span/2; # stop wavelength [nm]

wls = np.linspace(wl_start, wl_end, int((wl_end-wl_start)/wl_step+1))
voltages = np.linspace(v_start,v_end, int((v_end-v_start)/v_step+1))

pows = np.zeros((len(voltages),len(wls)))
print(pows)
