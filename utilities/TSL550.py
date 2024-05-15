# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 13:50:51 2020
Library function to control the TSL-550
NOTE: on the first installation please follow the manual at th efollowing folder
[to be added]
@author: sv18362
"""
import sys
import pyvisa as visa
#import visa
from math import *

def TSL550EnabledLD(TSL,state):
	if state==False:
		TSL.write('LF\r')
		print ('Led Off')
	else:
		TSL.write('LO\r')
		print ('Led On - wait till the laser turn on ~1 or 2 min - Led will stop blinking')

def TSL550Shutter(TSL,state):
	if state==False:
		TSL.write('SC\r')
		print ('Laser Off')
	else:
		TSL.write('SO\r')
		print ('Laser On')


def TSL550WL(TSL,wl,check):
	cmd='WA'+str(wl)+'\r'
	TSL.write(cmd)
	if check==True:
            print (TSL.query('WA'))
            wvl_c = (TSL.query('WA'))
            return wvl_c 
        
def TSL550P(TSL,P,unit):
	#pow='%.2' %P
   if unit == ' dBm':
       cmd='OP'+str(P)+'\r'
       TSL.write(cmd)
   elif unit == 'mW':
       cmd='LP'+str(P)+'\r'
       TSL.write(cmd)
   else:
       print('No unit selected script will stop')
       sys.exit()
       return
           
def TSL550Sweep_step_setup(TSL,wvl_SS,wvl_SE,step_wvl,dwell):
    TSL.query('SM3\r')
    TSL.query('SZ1\r')
    TSL.query('SS'+str(wvl_SS)+'\r')
    TSL.query('SE'+str(wvl_SE+'\r'))
    TSL.query('WW'+str(step_wvl)+'\r')
    TSL.query('SB'+str(dwell)+'\r')
    
