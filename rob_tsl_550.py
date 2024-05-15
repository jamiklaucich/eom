from utilities.ThorlabsPM100.ThorlabsPM100 import *
from utilities.TSL550 import *
import pyvisa as visa
from time import sleep

rm = visa.ResourceManager()
rm.list_resources()

pm_handle = rm.open_resource('USB0::0x1313::0x8072::1923224::INSTR')
power_meter = ThorlabsPM100(inst=pm_handle)

TSL550_Laser = rm.open_resource('ASRL3::INSTR',0)
TSL550_Laser.read_termination='\r'
TSL550WL(TSL550_Laser,1550,True)
sleep(1)
TSL550P(TSL550_Laser,5,'mW')
sleep(2)

wl_c = 1540.000;
span = 60.000;
Optical_power = 5.0 #dBm

wl_start = wl_c - span/2; # start wavelength [nm]
wl_end = wl_c + span/2; # stop wavalength [nm]
step = 0.25;#step [nm]

wl=wl_start
dwell_time = 1;
dBm=True
unit='mW'
if dBm==True:
	unit=' dBm'
	
sleep(1)
wllist=[]
pwlist=[]

read=power_meter.measure_power(wl)
print ('WL='+str(round(wl,4))+' nm	P='+str(read*1e3)+unit)

TSL550_Laser.clear()
m = 1
k = 0
ID = 'VN3299WF33_sysResp' # to change accordingly
file_name = str(str(ID)+'Opt_power'+str(Optical_power)+'dBm-wl_c'+str(wl_c)+'-wl_span'+str(span)+'-step'+str(step))
with open(file_name+'.csv', 'w+') as csvfile: # file name where store data
    out = csv.writer(csvfile,quotechar='|', quoting=csv.QUOTE_MINIMAL)
    
    while wl<wl_end:
        TSL550WL(TSL550_Laser,wl,True)
        #SetPmWL(power_meter,wl)
        sleep(0.5)
        read=power_meter.measure_power(wl)*1e3
        sleep(0.5)
        out.writerow([wl,read])
        wllist.append(wl)
        pwlist.append(read)
        wl+=step
        k = k + 1
        sleep(.200)
        if k == m*100:
                TSL550_Laser.clear()
                m = m+1
                print('cleared-----------------------------')
    plt.figure()
    plt.plot(wllist,pwlist)
    plt.show()
    
wllist=[]
pwlist=[]
wl = wl_start
print('Scan complete')