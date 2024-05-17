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
pm_handle = rm.open_resource('USB0::0x1313::0x8072::P2001769::INSTR')
power_meter = ThorlabsPM100(inst=pm_handle)
TSL550_Laser = ftdi.FTD2xx_helper("19100002")
keithley_2450 = rm.open_resource("USB0::0x05E6::0x2450::04610529::0::INSTR")

wl_c = 1550#nm
wl_span = 5#nm
wl_step = 0.001;#step [nm]

v_start = 0#V
v_end = 5#V
v_step = 0.5#V

Optical_power = 1.0 #dBm

measure_wait = 0.025#s time between switching laser wvl and measuring pow

wl_start = wl_c - wl_span/2; # start wavelength [nm]
wl_end = wl_c + wl_span/2; # stop wavelength [nm]

wls = np.linspace(wl_start, wl_end, int((wl_end-wl_start)/wl_step+1))
voltages = np.linsspace(v_start,v_end, int((v_end-v_start)/v_step+1))
keithley_2450.write(":ROUTe:TERMinals FRONt ")
keithley_2450.write(":SOURce:FUNCtion VOLTage")
keithley_2450.write("SOUR:VOLT:RANG:AUTO ON")
keithley_2450.write("SENS:CURR:RANG:AUTO ON")
keithley_2450.write("CURR:RANG:AUTO:LLIM 1e-4")
keithley_2450.write(":SOURce:VOLTage:RANGe 10")

ID = input("Enter Grating Designation")# to change accordingly
cur_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
folder_path = os.getcwd()+"/Data/TSl550_Sweep/"+cur_time
os.makedirs("{}{}".format(folder_path,ID), exist_ok=True)
file_name = str(str(ID)+'Opt_power'+str(Optical_power)+'dBm-wl_c'+str(wl_c)+'-wl_span'+str(span)+'-step'+str(step))

dBm=True
unit='mW'
if dBm==True:
	unit=' dBm'
	

#TSL550_Laser.clear()

pows = np.zeros_like(wls)

TSL550_Laser.Write("SO")#Open Shutter
TSL550_Laser.Write("WA{}".format(wls[0]))
time.sleep(1)
power_meter.read
init_time = time.time()

keithley_2450.write(":OUTP ON")
for j, wl in enumerate(wls):
      TSL550_Laser.Write("WA{}".format(wl))
      time.sleep(measure_wait)
      pows[j] = power_meter.read
      print("{} {}".format(wl, pows[i]))
      #print(progress_bar_time(j*len(appl_voltage)+i+1, len(laser_voltage*len(laser_power))+1, time.time()-laser_start_time))
keithley_2450.write(":OUTP OFF")
TSL550_Laser.Write("SC")#Close Shutter

sweep_df = pd.DataFrame({"Wavelength (nm)":wls, 
                        "Power (W)": pows})

sweep_df.to_csv("{}/{}.csv".format(folder_path,file_name), index=False)

fig = plt.figure()
ax = fig.add_subplot()
ax.plot(wls, pows)
ax.set_xlabel("Wavelengths (nm)")
ax.set_ylabel
fig.savefig("{}/wvl_sweep.png".format(folder_path, str(pow), cur_time))
plt.show()
    
