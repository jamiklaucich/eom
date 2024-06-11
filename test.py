import os
import clr
import sys
import time
import pyvisa as visa
import numpy as np
from utilities.ThorlabsPM100.ThorlabsPM100 import *
import serial

# data = '1530.54,-40.45DBM\r'
# data_=data.split(",")[0][:-4]
# print(data_)
assembly_path = r"C:/Users/qv18366/OneDrive - University of Bristol/Desktop/Santec/DLL"  # device-class path
sys.path.append(assembly_path)
ref = clr.AddReference(r"Santec_FTDI")
import Santec_FTDI as ftdi# Importing the main method from the DLL
# Calling the FTD2xx_helper class from the Santec_FTDI dll
ftdi_class = ftdi.FTD2xx_helper
TSL550_Laser = ftdi.FTD2xx_helper("17050019")

TSL550_Laser.Write("SC")