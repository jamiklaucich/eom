from utilities.ThorlabsPM100.ThorlabsPM100 import *
from datetime import datetime
import os
import numpy as np
import time
import pyvisa
import pandas as pd
import matplotlib.pyplot as plt

cur_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
folder_path = os.getcwd()+"/Data/PM100a_Repeat/"+cur_time
os.makedirs(folder_path, exist_ok=True)



rm = pyvisa.ResourceManager()

time_length = 200
measurements = np.zeros(time_length*1000)
times = np.zeros_like(measurements)
inst = rm.open_resource("USB0::0x1313::0x8078::P0007727::0::INSTR")
power_meter = ThorlabsPM100(inst=inst)
power_meter.sense.power.dc.range.auto = "ON"
start_time = time.perf_counter()
i=0
measure_time = 0

while (measure_time)<time_length:
    measurement = power_meter.read
    measurements[i] = measurement
    measure_time = time.perf_counter()-start_time
    if(i%150==0):
        print(f"#{i}:\t\t{measure_time:.1f}s\t/{time_length}s:\t{measurement:.6g}W")
    times[i] = measure_time
    i+=1

measurements=measurements[:i]
times = times[:i]
measure_df = pd.DataFrame({"Time (s)":times, 
                        "Power (W)": measurements})
measure_df.to_csv("{}/measure.csv".format(folder_path), index=False)
fig = plt.figure()
ax = fig.add_subplot()
ax.scatter(times, measurements)
fig.savefig("{}/measure.png".format(folder_path, str(pow), cur_time))
plt.show()