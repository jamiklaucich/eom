import os
import sys
import time
import clr
import pyvisa as visa
import pandas as pd
import numpy as np
from utilities.ThorlabsPM100.ThorlabsPM100 import *
from datetime import datetime
from res_pow_calib import *
from osa_calibration import *

import matplotlib.pyplot as plt

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

assembly_path = r"C:/Users/qv18366/OneDrive - University of Bristol/Desktop/Santec/DLL"  # device-class path
sys.path.append(assembly_path)
ref = clr.AddReference(r"Santec_FTDI")
import Santec_FTDI as ftdi# Importing the main method from the DLL
# Calling the FTD2xx_helper class from the Santec_FTDI dll
ftdi_class = ftdi.FTD2xx_helper
TSL550_Laser = ftdi.FTD2xx_helper("17050019")

rm = visa.ResourceManager()
print(rm.list_resources())
id_laser = rm.open_resource('ASRL4::INSTR',send_end=True, read_termination='\n')
id_laser.baud_rate= 115200
id_laser.timeout=2000
osa = rm.open_resource('ASRL5::INSTR',
                           write_termination = '\n',
                           read_termination = '\n')
osa.timeout=2000
power_meter = ThorlabsPM100(inst=rm.open_resource("USB0::0x1313::0x8078::P0007727::0::INSTR"))

id_laser.Write("SOUR:STATe 0")
TSL550_Laser.Write("SC")

pump_init_wl=1550.29
probe_init_wl = 1530.6
wl_span=0.25
mW=True
opow_start = 0.05
opow_end = 20.05
opow_step = 2.5

repeat_time=2
probe_wait=7#s
measure_wait = 7#s time between switching laser wvl and measuring pow
calib_measure_wait=0.25

probe_span=0.1#nm
probe_step=0.01#nm
probe_num=int(1+(probe_span)/probe_step)
probe_wl_d = np.linspace(-0.5*probe_span,0.5*probe_span, probe_num)

opow_num = int(1+(opow_end-opow_start)/opow_step)

opows = np.linspace(opow_start,opow_end,opow_num)
ID = input("Enter Device Designation: ")# to change accordingly
cur_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
folder_path = "{}/Data/osa_curr/{} {}".format(os.getcwd(),cur_time,ID)
os.makedirs("{}".format(folder_path), exist_ok=True)
file_name = f"{ID}-Opt_power{opow_start}dBm"
calib_flag=input("Enter any character to calibrate resonances with power input. Else previous resonance data is used")
if(calib_flag):
    res_wls,res_wls_df=res_pow_calib(TSL550_Laser, power_meter, opows, pump_init_wl, wl_span, wl_step = 0.01,measure_wait=calib_measure_wait, folder_path=folder_path )
    res_wls_df.to_csv("Resonant_Wavelengths.csv")
    input("Proceed?")
else:
    res_wls_df = pd.read_csv("Resonant_Wavelengths.csv")
    res_wls = np.array(res_wls_df["Wavelengths (nm)"].tolist())
    csv_pows = np.array(res_wls_df["Powers (mW)"].tolist())
    assert csv_pows.all() == opows.all()

res_wls_dl = res_wls-res_wls[0]
probe_wls = probe_init_wl+res_wls_dl
#wl_off, wl_ext=wavelength_calibration(osa, TSL550_Laser, pow_cal=False, l_wait=0.25, o_wait=2)
#print(f"{wl_off} {wl_ext}")
print(f"{res_wls}")


unit="dBm"
if (mW):
    unit="mW"

TSL550_Laser.Write(f"POW:UNIT {int(mW)}")
TSL550_Laser.Write("SO")#Open Shutter
TSL550_Laser.Write("WA{}".format(res_wls[0]))
id_laser.Write("SOUR:STATe 1")
#TSL550_Laser.clear()

# osa.write("*RST")

osa_init()
#print(osa.read())
#osa.write("PWR 1550")
pows = np.zeros_like(opows)
init_time = time.time()
for i, opow in enumerate(opows):
    TSL550_Laser.Write(f"LP{opow}")
    TSL550_Laser.Write(f"WA{res_wls[i]}")
    time.sleep(measure_wait)
    probe_sweep=np.zeros_like(probe_wl_d)
    for j,wl_d in enumerate(probe_wl_d):
        id_laser.write(f"WAV {probe_wls[i]+wl_d}")
        time.sleep(probe_wait)
        osa.write("SSI")
        sweep_done = osa_wait("ESR2?")
        osa.write("PKS PEAK")
        peak_done = osa_wait("ESR2?")
        osa.write("TMK?")
        osa_res = osa.read().split(",")
        probe_sweep[j] = 10**(float(osa_res[1][:-4])/10)
    pows[i] = np.min(probe_sweep)

# Split the string by comma
    print(f"{opow:.4f}mW \t{float(osa_res[0]):.4f}nm \t{pows[i]:.4g}W")
            #print(progress_bar_time(j*len(appl_voltage)+i+1, len(laser_voltage*len(laser_power))+1, time.time()-laser_start_time))

TSL550_Laser.Write("SC")#Close Shutter

sweep_df = pd.DataFrame({"Pump in Power (mW)":opows, 
                "Probe Out Power (W)": pows})
sweep_df.to_csv("{}/{}.csv".format(folder_path,file_name), index=False)
fig = plt.figure()
ax = fig.add_subplot()
ax.plot(opows, pows)
ax.set_xlabel("Pump in Power (mW)")
ax.set_ylabel("Probe Out Power (mW)")
fig.savefig("{}/wvl_sweep{}.png".format(folder_path, file_name))
plt.show()