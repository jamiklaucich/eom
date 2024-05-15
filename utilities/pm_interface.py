import visa
from ThorlabsPM100 import ThorlabsPM100, USBTMC
from math import *

def PmRead(power_meter,nounit=False,dBm=False):
	read=power_meter.read*10**3
	unit='mW'
	if dBm==True:
		read=10*log10(read)
		unit='dBm'
	if nounit==False:
		return str(read)+' '+unit
	else:
		return read

def SetPmWL(power_meter,wl,check=False):
	power_meter.sense.correction.wavelength=wl
	if check==True:
		print ('wl='+str(power_meter.sense.correction.wavelength))
