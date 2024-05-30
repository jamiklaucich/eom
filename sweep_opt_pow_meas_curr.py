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

wl = 1550.25#nm
v=1#V to sweep current out

mW=True
opow_start = 0.05
opow_end = 10
opow_step = 0.05

opow_num = int(2+(opow_end-opow_start)/opow_step)

opows = np.linspace(opow_start,opow_end,opow_num)

unit="dBm"
if (mW):
    unit="mW"

measure_wait = 0.5#s time between switching laser wvl and measuring pow
post_wait=0.1#s


keithley_2450.write(":ROUTe:TERMinals FRONt ")
keithley_2450.write(":SOURce:FUNCtion VOLTage")
keithley_2450.write("SOUR:VOLT:RANG:AUTO ON")
keithley_2450.write("SENS:CURR:RANG:AUTO ON")
keithley_2450.write("SENS:CURR:NPLCycles 1")
#keithley_2450.write("CURR:RANG:AUTO:LLIM 1e-4")
keithley_2450.write(":SOURce:VOLTage:RANGe 10")

ID = input("Enter Device Designation: ")# to change accordingly
cur_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
folder_path = (f"{os.getcwd()}/Data/Sweep_Opt_Meas_Curr/{cur_time} {ID}")
os.makedirs(f"{folder_path}", exist_ok=True)
file_name = f"{ID}-wl{wl}-opowstart{opow_start}-opowend{opow_end}-opowstep{opow_step}"



TSL550_Laser.Write(f"POW:UNIT {int(mW)}")
print(TSL550_Laser.Query("POW:UNIT?"))
#TSL550_Laser.clear()

current = np.zeros(len(opows))
pows = np.zeros(len(opows))

TSL550_Laser.Write("SO")#Open Shutter
TSL550_Laser.Write(f"WA{wl}")
time.sleep(1)
power_meter.read
keithley_2450.write(":OUTP ON")
keithley_2450.write("SOUR:VOLT {}".format(v))
init_time = time.time()
      
for i, opow in enumerate(opows):
      TSL550_Laser.Write(f"LP{opow}")
      time.sleep(measure_wait)
      current[i] = keithley_2450.query(':MEASure:CURRent? "defbuffer1"')
      pows[i] = power_meter.read
      time.sleep(post_wait)
      print("{:.4f}mW\t {:.4g}A\t {:.4g}W".format(opow, current[i], pows[i]))
      #print(progress_bar_time(j*len(appl_voltage)+i+1, len(laser_voltage*len(laser_power))+1, time.time()-laser_start_time))

keithley_2450.write(":OUTP OFF")
opows=opows*10**-3
sweep_df = pd.DataFrame({"Input Optical Power (nm)":opows, 
                  "Current (A)": current,
                  "Output Optical Power (W)": pows})
sweep_df.to_csv("{}/{}.csv".format(folder_path,file_name), index=False)
fig = plt.figure()
ax = fig.add_subplot()
ax.plot(opows, pows)
ax.set_xlabel("Optical Power In (W)")
ax.set_ylabel("Optical Power Out (W)")
fig.savefig("{}/wvl_sweep{}.png".format(folder_path, file_name))

fig = plt.figure()
ax = fig.add_subplot()
ax.plot(opows, current)
ax.set_xlabel("Optical Power In (mW)")
ax.set_ylabel("Current (A)")
fig.savefig("{}/cur_sweep{}.png".format(folder_path, file_name))

keithley_2450.write(":OUTP OFF")
TSL550_Laser.Write("SC")#Close Shutter