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

def frwd_bias_reset(voltage, delay, reset_current_lim, measure_current_lim):
    smu.source.limit(reset_current_lim)
    smu.write("SOUR:VOLT:LEV {}".format(voltage))
    smu.sense.current()
    time.sleep(delay)

    smu.source.limit(measure_current_lim)
    
def smu_source_sweep(smu, voltage, delay,  current_lim, nplc, repeats, funcs=None, func_args=None):
    smu.source.delay(delay)
    smu.source.limit(current_lim)
    smu.sense.nplc(nplc)
    smu.timeout(1000)
    appl_voltage = np.zeros_like(voltage)
    current = np.zeros_like(voltage)

    start_time = time.time()
    tripped=False
    with smu.output_enabled.set_to(True):
        for i, v in enumerate(voltage):
            if(tripped):
                appl_voltage = voltage[:i-1]
                current = current[:i-1]
                #remove the tripped measurement
                break
            rep_measure = np.zeros(repeats)
            for j in range(repeats):
                smu.source.voltage(v)
                appl_voltage[i] = smu.source.voltage()
                rep_measure[j] = smu.sense.current()
                if(smu.source.limit_tripped()):
                    tripped=True
                if(frwd_reset):
                    frwd_bias_reset(*reset_vars)
            current[i] = sum(rep_measure)/repeats
            print("Voltage: {:.4f}V ".format(v)+progress_bar_time(i+1, len(voltage)+1, time.time()-start_time))

    return appl_voltage, current


dv = 0.1 #V
#voltage steps

rev_bias_start = 11.5 #V
rev_bias_end = 0 #V
frwd_bias_start = 0 #V
frwd_bias_end = 11.5 #V

meas_delay = 0.1#s
current_limit = 100E-6#A
nplc = 1
num_repeats=1

frwd_reset=False
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
#Keithley 2450 VISA address

reset_delay=1.0#s length of time to run in forward bias to reset DUT
initial_reset_delay = 20#s
reset_current_limit = 100E-6#A
reset_voltage =-1#V

reset_vars = [reset_voltage, reset_delay, reset_current_limit, current_limit]
initial_reset_vars = [reset_voltage, initial_reset_delay, reset_current_limit, current_limit]

rev_num = int(1+abs(rev_bias_end-rev_bias_start)/dv)
rev_voltage = np.linspace(rev_bias_start, rev_bias_end, rev_num)
frwd_num = int(1+abs(frwd_bias_end-frwd_bias_start)/dv)
frwd_voltage = np.linspace(frwd_bias_start, frwd_bias_end, frwd_num)

with smu.output_enabled.set_to(True):
    print("\nResetting device for {}s".format(initial_reset_delay))
    if(frwd_reset):
        frwd_bias_reset(*initial_reset_vars)

frwd_appl_voltage, frwd_current = smu_source_sweep(smu,frwd_voltage, meas_delay,  current_limit, nplc, num_repeats)
rev_appl_voltage, rev_current = smu_source_sweep(smu,rev_voltage, meas_delay,  current_limit, nplc, num_repeats)


comb_voltage = np.concatenate((rev_appl_voltage, frwd_appl_voltage))
comb_current = np. concatenate((rev_current, frwd_current))
# comb_voltage = frwd_appl_voltage
# comb_current = frwd_current
#I-V plot
# root = Tk()
# root.attributes('-topmost', True)  # Display the dialog in the foreground.
# root.iconify()  # Hide the little window.
# initial_dir = os.getcwd()+"\Data\Source Sweep"
# file_path = filedialog.asksaveasfilename(filetypes=[("csv", ".csv")], 
#                                          defaultextension=".csv", 
#                                          initialdir=initial_dir, 
#                                          initialfile="Current.csv")
# root.destroy()
current_df=pd.DataFrame({"Voltage (V)":comb_voltage, "Current": comb_current})
current_df.to_csv("{}/{}source_sweep.csv".format(folder_path,cur_time), index=False)

fig = plt.figure()
ax = fig.add_subplot()
ax.scatter(comb_voltage, comb_current*1e6)
ax.set_xlabel("Voltage(V)")
ax.set_ylabel("Current (µA)")
fig.savefig("{}/IV{}.png".format(folder_path, cur_time))
