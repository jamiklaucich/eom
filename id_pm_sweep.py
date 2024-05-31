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


rm = visa.ResourceManager()
rm.list_resources()

pm_handle = rm.open_resource("USB0::0x1313::0x8078::P0007727::0::INSTR")
power_meter = ThorlabsPM100(inst=pm_handle)
id_laser = rm.open_resource('ASRL4::INSTR',send_end=True, read_termination='\n')
id_laser.baud_rate= 115200
id_laser.timeout=2000


wl_c = 1550.235#nm
span = 1.5#nm
step = 0.01;#step [nm]

Optical_power = 1.0 #dBm

measure_wait = 7.0#s time between switching laser wvl and measuring pow

wl_start = wl_c - span/2; # start wavelength [nm]
wl_end = wl_c + span/2; # stop wavelength [nm]

wls = np.linspace(wl_start, wl_end, int((wl_end-wl_start)/step+1))

ID = input("Enter Grating Designation: ")# to change accordingly
cur_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
folder_path = "{}/Data/ID_Sweep/{} {}".format(os.getcwd(),cur_time,ID)
os.makedirs("{}".format(folder_path), exist_ok=True)
file_name = str(str(ID)+'Opt_power'+str(Optical_power)+'dBm-wl_c'+str(wl_c)+'-wl_span'+str(span)+'-step'+str(step))

dBm=True
unit='mW'
if dBm==True:
	unit=' dBm'
	

#TSL550_Laser.clear()

pows = np.zeros_like(wls)

id_laser.write(f"WAV {wls[0]}")
time.sleep(1)
power_meter.read
init_time = time.time()
for i, wl in enumerate(wls):
      id_laser.write(f"WAV {wl}")
      time.sleep(measure_wait)
      pows[i] = power_meter.read
      print(f"{wl:.4f}nm\t{pows[i]:.4g}W")
      #print(progress_bar_time(j*len(appl_voltage)+i+1, len(laser_voltage*len(laser_power))+1, time.time()-laser_start_time))


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
    
