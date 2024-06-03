import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import time
import sys
import os
from tkinter import filedialog, Tk
from qcodes.instrument_drivers.Keithley import Keithley2450
from datetime import datetime
from utilities import measure_utils
from utilities.qcodes_utils import *
import clr

def frwd_bias_reset(voltage, delay, reset_current_lim, measure_current_lim):
    smu.source.limit(reset_current_lim)
    smu.write("SOUR:VOLT:LEV {}".format(voltage))
    smu.sense.current()
    time.sleep(delay)

    smu.source.limit(measure_current_lim)
    
def smu_source_sweep(smu, voltage, delay,  current_lim, nplc, repeats, funcs=None, func_args=None):
    

    start_time = time.time()
    tripped=False
    with smu.output_enabled.set_to(True):
        for i, v in enumerate(voltage):
            

    return appl_voltage, current

assembly_path = r"C:/Users/qv18366/OneDrive - University of Bristol/Desktop/Santec/DLL"  # device-class path
sys.path.append(assembly_path)
ref = clr.AddReference(r"Santec_FTDI")
import Santec_FTDI as ftdi# Importing the main method from the DLL
# Calling the FTD2xx_helper class from the Santec_FTDI dll
ftdi_class = ftdi.FTD2xx_helper
TSL550_Laser = ftdi.FTD2xx_helper("19100002")

wl_c = 1550.25#nm

bias_start = 0 #V
bias_end = 13 #V
dv = 0.1 #V

unit_gain_voltage=1#V

meas_delay = 0.1#s
current_limit = 100E-6#A
nplc = 1
num_repeats=1
ID = input("Enter Grating Designation: ")# to change accordingly
cur_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
folder_path = os.getcwd()+"/Data/voltage_sweep/"+cur_time+ID
os.makedirs(folder_path, exist_ok=True)

smu = Keithley2450("keithley", "USB0::0x05E6::0x2450::04610529::0::INSTR")
smu.reset()
smu.terminals("front")
smu.source.function("voltage")
smu.source.auto_range(False)
smu.sense.auto_range(True)
smu.write("CURR:RANG:AUTO:LLIM 1e-4")
smu.write(":SOURce:VOLTage:RANGe 10")
smu.source.read_back_enabled(True)
smu.source.delay(meas_delay)
smu.source.limit(current_limit)
smu.sense.nplc(nplc)
smu.timeout(1000)


reset_delay=1.0#s length of time to run in forward bias to reset DUT
initial_reset_delay = 20#s
reset_current_limit = 100E-6#A
reset_voltage =-1#V

reset_vars = [reset_voltage, reset_delay, reset_current_limit, current_limit]
initial_reset_vars = [reset_voltage, initial_reset_delay, reset_current_limit, current_limit]

voltage_num = int(1+abs(bias_end-bias_start)/dv)
voltage = np.linspace(bias_start, bias_end, voltage_num)

dual_voltages = np.array([voltage, voltage])
dual_currents = np.zeros_like(dual_voltages)

TSL550_Laser.Write("SC")#Close Shutter
with smu.output_enabled.set_to(True):
    print("\nResetting device for {}s".format(initial_reset_delay))
    frwd_bias_reset(*initial_reset_vars)
    start_time = time.time()
    for i, voltages in enumerate(dual_voltages):
        for j, volt in enumerate(voltages):
            if(tripped):
                    dual_voltages[i] = dual_voltages[i][:j-1]
                    current = current[:i-1]
                    #remove the tripped measurement
                    break
            smu.source.voltage(volt)
            dual_voltages[i][j] = smu.source.voltage()
            dual_currents[i][j] = smu.sense.current()
            if(smu.source.limit_tripped()):
                        tripped=True
            print("Voltage: {:.4f}V ".format(volt)+progress_bar_time(i+1, len(dual_voltages[i])+1, time.time()-start_time))
            frwd_bias_reset(*reset_vars)
        TSL550_Laser.Write("SO")#Open Shutter
    TSL550_Laser.Write("SC")#Close Shutter

dark_voltages = dual_voltages[0]
light_voltages = dual_voltages[1]
dark_currents = dual_currents[0]
light_currents = dual_currents[1]

unit_gain_volt_index = np.argmin(np.abs(voltages - unit_gain_voltage))
gain = (light_currents-dark_currents)/(light_currents[unit_gain_volt_index]-dark_currents[unit_gain_volt_index])

dark_current_df=pd.DataFrame({"Voltage (V)":voltages, "Current (A)": dark_currents})
dark_current_df.to_csv(f"{folder_path}/{cur_time}dark_IV.csv", index=False)

light_current_df=pd.DataFrame({"Voltage (V)":voltages, "Current (A)": dark_currents})
light_current_df.to_csv(f"{folder_path}/{cur_time}light_IV.csv", index=False)

gain_df = pd.DataFrame({"Voltage (V)":voltages, "Gain": gain})
gain_df.to_csv(f"{folder_path}/{cur_time}gain.csv", index=False)

fig = plt.figure()
ax = fig.add_subplot()
ax.scatter(voltages, dark_currents)
ax.set_xlabel("Voltage(V)")
ax.set_ylabel("Current (A)")
fig.savefig("{}/dark_IV{}.png".format(folder_path, cur_time))

fig = plt.figure()
ax = fig.add_subplot()
ax.scatter(voltages, light_currents)
ax.set_xlabel("Voltage(V)")
ax.set_ylabel("Current (A)")
fig.savefig("{}/dark_IV{}.png".format(folder_path, cur_time))

fig = plt.figure()
ax = fig.add_subplot()
ax.scatter(voltages, gain)
ax.set_xlabel("Voltage(V)")
ax.set_ylabel("Gain")
fig.savefig(f"{folder_path}/Gain{cur_time}.png")
