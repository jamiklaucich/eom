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

wl_c = 1550.25#nm
wl_span = 1.5#nm
wl_step = 0.01;#step [nm]

mW=True
opow_start = 0.05
opow_end = 10.05
opow_step = 2.5

opow_num = int(2+(opow_end-opow_start)/opow_step)

opows = np.linspace(opow_start,opow_end,opow_num)

measure_wait = 0.25#s time between switching laser wvl and measuring pow

wl_start = wl_c - wl_span/2; # start wavelength [nm]
wl_end = wl_c + wl_span/2; # stop wavelength [nm]

wls = np.linspace(wl_start, wl_end, int((wl_end-wl_start)/wl_step+1))


ID = input("Enter Device Designation: ")# to change accordingly
cur_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
folder_path = "{}/Data/sweep_opt_wav_meas_opt/{} {}".format(os.getcwd(),cur_time,ID)
os.makedirs("{}".format(folder_path), exist_ok=True)
file_names = [f"{ID}-Opt_power{opt}dBm-wl_c{wl_c}-wl_span{wl_span}-step{wl_step}"
              for opt in opows]

unit="dBm"
if (mW):
    unit="mW"
#TSL550_Laser.clear()

pows = np.zeros((len(opows),len(wls)))
sweep_dfs = np.zeros_like(opows, dtype=object)

TSL550_Laser.Write(f"POW:UNIT {int(mW)}")
TSL550_Laser.Write("SO")#Open Shutter
TSL550_Laser.Write("WA{}".format(wls[0]))
time.sleep(1)
power_meter.read

init_time = time.time()
for i, opow in enumerate(opows):
      TSL550_Laser.Write(f"LP{opow}")
      time.sleep(measure_wait)
      for j, wl in enumerate(wls):
            TSL550_Laser.Write("WA{}".format(wl))
            time.sleep(measure_wait)
            pows[i][j] = power_meter.read
            print(f"{opow:.4f}mW \t{wl:.4f}nm \t{pows[i][j]:.4g}W")
            #print(progress_bar_time(j*len(appl_voltage)+i+1, len(laser_voltage*len(laser_power))+1, time.time()-laser_start_time))
      sweep_dfs[i] = pd.DataFrame({"Wavelength (nm)":wls, 
                        "Power (W)": pows[i]})
      sweep_dfs[i].to_csv("{}/{}.csv".format(folder_path,file_names[i]), index=False)
      fig = plt.figure()
      ax = fig.add_subplot()
      ax.plot(wls, pows[i])
      ax.set_xlabel("Wavelengths (nm)")
      ax.set_ylabel("Optical Power (W)")
      fig.savefig("{}/wvl_sweep{}.png".format(folder_path, file_names[i]))

TSL550_Laser.Write("SC")#Close Shutter


    
