import os
import clr
import sys
import time
import pyvisa as visa
import numpy as np
from utilities.ThorlabsPM100.ThorlabsPM100 import *

# mW=True
# opow_start = 0.05
# opow_end = 10
# opow_step = 0.05

# opow_num = int(2+((opow_end-opow_start)/opow_step))

# opows = np.linspace(opow_start,opow_end,opow_num)
# print(opows)
rm = visa.ResourceManager()
instrument = rm.open_resource('ASRL4::INSTR',send_end=True, read_termination='\n')
instrument.baud_rate= 115200
instrument.timeout=2000
#instrument.chunk_size = 1002400
#instrument.write(":SYS:ECHO 1;")
# print(instrument.write_termination)
# instrument.write(":CLS;\r")
# # #instrument.write(":*RST;")
instrument.write("WAV 1540;")
instrument.write("pow 14;")
instrument.write("stat 1;")
instrument.write("busy?;")
instrument.write("STATe 0")
#instrument.write(":CARD:INFO;")
#instrument.write("*IDN?;")
# instrument.write(":READ?;")
# print(instrument.session)
time.sleep(0.5)
flag=True
while(flag):
    try:
        print(instrument.read_bytes(1))
    except:
         flag=False
#print(instrument.read_raw())

# power_meter = ThorlabsPM100(inst=pm_handle)
# wl_c = 1550#nm
# wl_span = 1#nm
# wl_step = 1;#step [nm]

# v_start = 0#V
# v_end = 2#V
# v_step = 0.5#V

# Optical_power = 1.0 #dBm

# measure_wait = 0.025#s time between switching laser wvl and measuring pow

# wl_start = wl_c - wl_span/2; # start wavelength [nm]
# wl_end = wl_c + wl_span/2; # stop wavelength [nm]

# wls = np.linspace(wl_start, wl_end, int((wl_end-wl_start)/wl_step+1))
# voltages = np.linspace(v_start,v_end, int((v_end-v_start)/v_step+1))

# pows = np.zeros((len(voltages),len(wls)))
# print(pows)
