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

wl_c = 1550.25#nm
wl_span = 1#nm
wl_step = 0.01#nm
reverse=False#Flag to go from high wav to low

v=11.55#V to sweep current out

mW=True
opow_start = 0.1
opow_end = 10.1
opow_step = 5

opow_num = int(1+(opow_end-opow_start)/opow_step)
opows = np.linspace(opow_start,opow_end,opow_num)

wl_start = wl_c - wl_span/2; # start wavelength [nm]
wl_end = wl_c + wl_span/2; # stop wavelength [nm]
if(reverse):
    temp=wl_start
    wl_start=wl_end
    wl_end=temp

wls = np.linspace(wl_start, wl_end, int((abs(wl_end-wl_start)/wl_step)+1))

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

file_names = [f"{ID}-voltage{v}-Opt_pow{opow}-wl_c{wl_c}-wl_span{wl_span}" 
              for opow in opows]

TSL550_Laser.Write(f"POW:UNIT {int(mW)}")#set power unit (0-dbm, 1-mW)

current = np.zeros((len(opows),len(wls)))
pows = np.zeros((len(opows),len(wls)))
sweep_dfs = np.zeros_like(opows, dtype=object)

TSL550_Laser.Write("SO")#Open Shutter
TSL550_Laser.Write(f"WA{wls[0]}")
time.sleep(1)
power_meter.read
keithley_2450.write(":OUTP ON")
keithley_2450.write("SOUR:VOLT {}".format(v))
init_time = time.time()
      
for i, opow in enumerate(opows):
    TSL550_Laser.Write(f"LP{opow}")
    for j, wl in enumerate(wls):
        TSL550_Laser.Write("WA{}".format(wl))
        time.sleep(measure_wait)
        current_meas = float(keithley_2450.query(':MEASure:CURRent? "defbuffer1"'))
        pow_meas = float(power_meter.read)
        current[i][j] = current_meas
        pows[i][j] = pow_meas
        print(f"{opow:.4f}mW\t{wl}nm\t{current_meas:.4g}A\t{pow_meas:.4g}W")
        time.sleep(post_wait)
        #print(progress_bar_time(j*len(appl_voltage)+i+1, len(laser_voltage*len(laser_power))+1, time.time()-laser_start_time))

    opows[i]=opows[i]*10**-3
    sweep_dfs[i] = pd.DataFrame({"Wavelength (nm)":wls, 
                  "Current (A)": current[i],
                  "Output Optical Power (W)": pows[i]})
    sweep_dfs[i].to_csv(f"{folder_path}/{file_names[i]}.csv", index=False)
    fig = plt.figure()
    ax = fig.add_subplot()
    ax.plot(wls, pows[i])
    ax.set_xlabel("Wavelength (nm)")
    ax.set_ylabel("Optical Power Out (W)")
    fig.savefig(f"{folder_path}/wvl_sweep{file_names[i]}.png")

    fig = plt.figure()
    ax = fig.add_subplot()
    ax.plot(wls, current[i])
    ax.set_xlabel("Wavelength (nm)")
    ax.set_ylabel("Current (A)")
    fig.savefig(f"{folder_path}/cur_sweep{file_names[i]}.png")

keithley_2450.write(":OUTP OFF")
TSL550_Laser.Write("SC")#Close Shutter


    
