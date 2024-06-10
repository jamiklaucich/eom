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

wl_c = 1549.3#nm
opt_pow=1#mW

bias_start = 0 #V
bias_end = 12.0 #V
dv = 0.25 #V

unit_gain_voltage=1#V

meas_delay = 0.1#s
current_limit = 100E-6#A
nplc = 3
num_repeats=1

reset_delay=2.0#s length of time to run in forward bias to reset DUT
initial_reset_delay = 20#s
reset_current_limit = 100E-6#A
reset_voltage =-1#V

assembly_path = r"C:/Users/qv18366/OneDrive - University of Bristol/Desktop/Santec/DLL"  # device-class path
sys.path.append(assembly_path)
ref = clr.AddReference(r"Santec_FTDI")
import Santec_FTDI as ftdi# Importing the main method from the DLL
# Calling the FTD2xx_helper class from the Santec_FTDI dll
ftdi_class = ftdi.FTD2xx_helper
TSL550_Laser = ftdi.FTD2xx_helper("19100002")

ID = input("Enter Grating Designation: ")# to change accordingly
cur_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
folder_path = os.getcwd()+"/Data/Santec_Gain/"+cur_time+ID
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


reset_vars = [reset_voltage, reset_delay, reset_current_limit, current_limit]
initial_reset_vars = [reset_voltage, initial_reset_delay, reset_current_limit, current_limit]

voltage_num = int(1+abs(bias_end-bias_start)/dv)
voltage = np.linspace(bias_start, bias_end, voltage_num)

dual_voltages = np.array([voltage, voltage])
dual_currents = np.zeros_like(dual_voltages)
TSL550_Laser.Write(f"LP{opt_pow}")
TSL550_Laser.Write("SC")#Close Shutter
with smu.output_enabled.set_to(True):
    start_time = time.time()
    for i, voltages in enumerate(dual_voltages):
        print("\nResetting device for {}s".format(initial_reset_delay))
        frwd_bias_reset(*initial_reset_vars)
        start_time+=reset_delay#compensate time estimate by reset delay
        tripped=False
        smu.source.voltage(0)
        smu.sense.current()
        for j, volt in enumerate(voltages):
            if(tripped):
                    dual_voltages[i] = dual_voltages[i][:j-1]
                    current = current[:i-1]
                    #remove the tripped measurement
                    break
            smu.source.voltage(volt)
            dual_voltages[i][j] = smu.source.voltage()
            meas_curr = smu.sense.current()
            dual_currents[i][j] = meas_curr
            if(smu.source.limit_tripped()):
                        tripped=True
            print(f"V:{volt:.4f}V\tI:{meas_curr:.4g}A\t"+progress_bar_time(i*len(dual_voltages[i])+j+1, 2*len(dual_voltages[i])+1, time.time()-start_time))
            frwd_bias_reset(*reset_vars)
        TSL550_Laser.Write("SO")#Open Shutter
    TSL550_Laser.Write("SC")#Close Shutter

dark_voltages = dual_voltages[0]
light_voltages = dual_voltages[1]
dark_currents = dual_currents[0]
light_currents = dual_currents[1]

unit_gain_volt_index = np.argmin(np.abs(voltages - unit_gain_voltage))
photocurrents = light_currents-dark_currents
gain = (photocurrents)/(photocurrents[unit_gain_volt_index])

current_df=pd.DataFrame({"Voltage (V)":voltages, 
                         "Dark Current (A)": dark_currents, 
                         "Light Current (A)": light_currents,
                         "Photocurrent (A)": photocurrents})
current_df.to_csv(f"{folder_path}/{cur_time}IV.csv", index=False)

gain_df = pd.DataFrame({"Voltage (V)":voltages, "Gain": gain})
gain_df.to_csv(f"{folder_path}/{cur_time}gain.csv", index=False)

fig = plt.figure()
ax = fig.add_subplot()
ax.scatter(voltages, dark_currents)
ax.set_xlabel("Voltage(V)")
ax.set_ylabel("Dark Current (A)")
fig.savefig("{}/dark_IV{}.png".format(folder_path, cur_time))

fig = plt.figure()
ax = fig.add_subplot()
ax.scatter(voltages, light_currents)
ax.set_xlabel("Voltage(V)")
ax.set_ylabel("Light Current (A)")
fig.savefig("{}/Light_IV{}.png".format(folder_path, cur_time))

fig = plt.figure()
ax = fig.add_subplot()
ax.scatter(voltages, photocurrents)
ax.set_xlabel("Voltage(V)")
ax.set_ylabel("Photocurrent (A)")
fig.savefig("{}/Photo_IV{}.png".format(folder_path, cur_time))

fig = plt.figure()
ax = fig.add_subplot()
ax.scatter(voltages, gain)
ax.set_xlabel("Voltage(V)")
ax.set_ylabel("Gain")
fig.savefig(f"{folder_path}/Gain{cur_time}.png")
