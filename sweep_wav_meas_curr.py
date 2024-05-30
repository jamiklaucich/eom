from utilities.ThorlabsPM100.ThorlabsPM100 import *
from utilities.TSL550 import *
from utilities.qcodes_utils import *
import pyvisa as visa
import numpy as np
import pandas as pd
from datetime import datetime
import os
import matplotlib.pyplot as plt
import clr
import sys
import time

# Checking and Accessing the DLL (Santec_FTDI) [make sure the DLLs are in the same directory as the script]
assembly_path = r"C:/Users/qv18366/OneDrive - University of Bristol/Desktop/Santec/DLL"  # device-class path
sys.path.append(assembly_path)
ref = clr.AddReference(r"Santec_FTDI")
import Santec_FTDI as ftdi# Importing the main method from the DLL
# Calling the FTD2xx_helper class from the Santec_FTDI dll
ftdi_class = ftdi.FTD2xx_helper

rm = visa.ResourceManager()
rm.list_resources()
pm_handle = rm.open_resource("USB0::0x1313::0x8078::P0007727::0::INSTR")
power_meter = ThorlabsPM100(inst=pm_handle)
TSL550_Laser = ftdi.FTD2xx_helper("19100002")
keithley_2450 = rm.open_resource("USB0::0x05E6::0x2450::04610529::0::INSTR")

wl_c = 1540#nm
wl_span = 40#nm
wl_step = 0.01#nm

v=1#V to sweep current out

Optical_power = 0 #dBm

measure_wait = 0.25#s time between switching laser wvl and measuring pow

wl_start = wl_c - wl_span/2; # start wavelength [nm]
wl_end = wl_c + wl_span/2; # stop wavelength [nm]

wls = np.linspace(wl_start, wl_end, int((wl_end-wl_start)/wl_step+1))

keithley_2450.write(":ROUTe:TERMinals FRONt ")
keithley_2450.write(":SOURce:FUNCtion VOLTage")
keithley_2450.write("SOUR:VOLT:RANG:AUTO ON")
keithley_2450.write("SENS:CURR:RANG:AUTO ON")
keithley_2450.write("SENS:CURR:NPLCycles 1")
#keithley_2450.write("CURR:RANG:AUTO:LLIM 1e-4")
keithley_2450.write(":SOURce:VOLTage:RANGe 10")

ID = input("Enter Device Designation: ")# to change accordingly
cur_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
folder_path = "{}/Data/Sweep_Wav_Meas_Curr/{} {}".format(os.getcwd(),cur_time,ID)
os.makedirs("{}".format(folder_path), exist_ok=True)
file_name = "{}-Opt_power{}dBm-wl_c{}-wl_span{}-step{}".format(ID, Optical_power, wl_c, wl_span, wl_step) 

dBm=True
unit='mW'
if dBm==True:
	unit=' dBm'
	

#TSL550_Laser.clear()

current = np.zeros(len(wls))
pows = np.zeros(len(wls))

TSL550_Laser.Write("SO")#Open Shutter
TSL550_Laser.Write("WA{}".format(wls[0]))
time.sleep(1)
power_meter.read
keithley_2450.write(":OUTP ON")
keithley_2450.write("SOUR:VOLT {}".format(v))
init_time = time.time()
      
for i, wl in enumerate(wls):
      TSL550_Laser.Write("WA{}".format(wl))
      time.sleep(measure_wait)
      current[i] = keithley_2450.query(':MEASure:CURRent? "defbuffer1"')
      pows[i] = power_meter.read
      print("{:.4f}nm\t {:.4g}A\t {:.4g}W".format(wl, current[i], pows[i]))
      #print(progress_bar_time(j*len(appl_voltage)+i+1, len(laser_voltage*len(laser_power))+1, time.time()-laser_start_time))

keithley_2450.write(":OUTP OFF")

sweep_df = pd.DataFrame({"Wavelength (nm)":wls, 
                  "Current (A)": current,
                  "Power (W)": pows})
sweep_df.to_csv("{}/{}.csv".format(folder_path,file_name), index=False)
fig = plt.figure()
ax = fig.add_subplot()
ax.plot(wls, pows)
ax.set_xlabel("Wavelengths (nm)")
ax.set_ylabel("Optical Power (W)")
fig.savefig("{}/wvl_sweep{}.png".format(folder_path, file_name))

fig = plt.figure()
ax = fig.add_subplot()
ax.plot(wls, current)
ax.set_xlabel("Wavelengths (nm)")
ax.set_ylabel("Current (A)")
fig.savefig("{}/cur_sweep{}.png".format(folder_path, file_name))

keithley_2450.write(":OUTP OFF")
TSL550_Laser.Write("SC")#Close Shutter


    
