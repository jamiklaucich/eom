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
TSL550_Laser = ftdi.FTD2xx_helper("19100002")



rm = visa.ResourceManager()
print(rm.list_resources())
osa = rm.open_resource('ASRL5::INSTR',
                           write_termination = '\n',
                           read_termination = '\n')
osa.timeout=2000
power_meter = ThorlabsPM100(inst=rm.open_resource("USB0::0x1313::0x8078::P0007727::0::INSTR"))

wl_off, wl_ext=wavelength_calibration(osa, TSL550_Laser, pow_cal=False, l_wait=0.5, o_wait=2, wl_span=2):

wl=1550.44
mW=True
opow_start = 0.05
opow_end = 20.05
opow_step = 1.0

repeat_time=2

opow_num = int(1+(opow_end-opow_start)/opow_step)

opows = np.linspace(opow_start,opow_end,opow_num)
measure_wait = 0.25#s time between switching laser wvl and measuring pow

res_wls=res_pow_calib(TSL550_Laser, power_meter, opows, wl_init=1550, wl_span=1, wl_step = 0.01,measure_wait=1 )
res_wls
# ID = input("Enter Device Designation: ")# to change accordingly
# cur_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
# folder_path = "{}/Data/osa_curr/{} {}".format(os.getcwd(),cur_time,ID)
# os.makedirs("{}".format(folder_path), exist_ok=True)
# file_name = f"{ID}-Opt_power{opow_start}dBm"

# unit="dBm"
# if (mW):
#     unit="mW"

# TSL550_Laser.Write(f"POW:UNIT {int(mW)}")
# TSL550_Laser.Write("SO")#Open Shutter
# TSL550_Laser.Write("WA{}".format(wl))
# #TSL550_Laser.clear()

# # osa.write("*RST")

# osa_init()
# #print(osa.read())
# #osa.write("PWR 1550")
# pows = np.zeros_like(opows)
# init_time = time.time()
# for i, opow in enumerate(opows):
#     TSL550_Laser.Write(f"LP{opow}")
#     time.sleep(measure_wait)
#     osa.write("SSI")
#     sweep_done = osa_wait("ESR2?")
#     osa.write("PKS PEAK")
#     peak_done = osa_wait("ESR2?")
#     osa.write("TMK?")
#     osa_res = osa.read().split(",")
#     pows[i] = 10**(float(osa_res[1][:-4])/10)

# # Split the string by comma
#     print(f"{opow:.4f}mW \t{float(osa_res[0]):.4f}nm \t{pows[i]:.4g}W")
#             #print(progress_bar_time(j*len(appl_voltage)+i+1, len(laser_voltage*len(laser_power))+1, time.time()-laser_start_time))

# TSL550_Laser.Write("SC")#Close Shutter

# sweep_df = pd.DataFrame({"Pump in Power (mW)":opows, 
#                 "Probe Out Power (W)": pows})
# sweep_df.to_csv("{}/{}.csv".format(folder_path,file_name), index=False)
# fig = plt.figure()
# ax = fig.add_subplot()
# ax.plot(opows, pows)
# ax.set_xlabel("Pump in Power (mW)")
# ax.set_ylabel("Probe Out Power (mW)")
# fig.savefig("{}/wvl_sweep{}.png".format(folder_path, file_name))
# plt.show()