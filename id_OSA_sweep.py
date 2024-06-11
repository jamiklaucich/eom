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

def osa_wait(command):
    comp=0
    time.sleep(repeat_time)
    while not comp:
        osa.write(command)
        comp=int(osa.read())
    return(comp)

def osa_init():
    osa.write("*IDN?")
    osa.write("BUZ OFF")
    osa.write("EMK")



rm = visa.ResourceManager()
rm.list_resources()

pm_handle = rm.open_resource("USB0::0x1313::0x8078::P0007727::0::INSTR")
power_meter = ThorlabsPM100(inst=pm_handle)
id_laser = rm.open_resource('ASRL4::INSTR',send_end=True, read_termination='\n')
id_laser.baud_rate= 115200
id_laser.timeout=2000
osa = rm.open_resource('ASRL5::INSTR',
                           write_termination = '\n',
                           read_termination = '\n')
osa.timeout=2000

wl_c = 1530.5#nm
span = .1#nm
step = 0.01;#step [nm]

Optical_power = 1.0 #dBm

measure_wait = 7.0#s time between switching laser wvl and measuring pow
repeat_time=.8

wl_start = wl_c - span/2; # start wavelength [nm]
wl_end = wl_c + span/2; # stop wavelength [nm]

wls = np.linspace(wl_start, wl_end, int((wl_end-wl_start)/step+1))

ID = input("Enter Grating Designation: ")# to change accordingly
cur_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
folder_path = "{}/Data/ID_OSA_Sweep/{} {}".format(os.getcwd(),cur_time,ID)
os.makedirs("{}".format(folder_path), exist_ok=True)
file_name = str(str(ID)+'Opt_power'+str(Optical_power)+'dBm-wl_c'+str(wl_c)+'-wl_span'+str(span)+'-step'+str(step))

dBm=True
unit='mW'
if dBm==True:
	unit=' dBm'
	
osa_init()
#TSL550_Laser.clear()
osa.write(f"CNT {wl_c}")
osa.write(f"SPN {span*2}")
pows = np.zeros_like(wls)

id_laser.write(f"WAV {wls[0]}")
time.sleep(1)
power_meter.read
init_time = time.time()
for i, wl in enumerate(wls):
      id_laser.write(f"WAV {wl}")
      time.sleep(measure_wait)
      osa.write("SSI")
      sweep_done = osa_wait("ESR2?")
      osa.write("PKS PEAK")
      peak_done = osa_wait("ESR2?")
      osa.write("TMK?")
      pows[i] = 10**(float(osa.read().split(",")[1][:-4])/10)
      print(f"{wl:.4f}nm\t{pows[i]:.4g}W")
      #print(progress_bar_time(j*len(appl_voltage)+i+1, len(laser_voltage*len(laser_power))+1, time.time()-laser_start_time))


sweep_df = pd.DataFrame({"Wavelength (nm)":wls, 
                        "Power (mW)": pows})

sweep_df.to_csv("{}/{}.csv".format(folder_path,file_name), index=False)

fig = plt.figure()
ax = fig.add_subplot()
ax.plot(wls, pows)
ax.set_xlabel("Wavelengths (nm)")
ax.set_ylabel
fig.savefig("{}/wvl_sweep.png".format(folder_path, str(pow), cur_time))
plt.show()
    
