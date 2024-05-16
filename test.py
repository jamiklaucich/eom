import os
import clr
import sys
import time

# Checking and Accessing the DLL (Santec_FTDI) [make sure the DLLs are in the same directory as the script]
assembly_path = r"C:/Users/qv18366/OneDrive - University of Bristol/Desktop/Santec/DLL"  # device-class path
sys.path.append(assembly_path)
ref = clr.AddReference(r"Santec_FTDI")

# Importing the main method from the DLL
import Santec_FTDI as ftdi

# Calling the FTD2xx_helper class from the Santec_FTDI dll
ftdi_class = ftdi.FTD2xx_helper

# ListDevices() returns the list of all Santec instruments
list_of_devices = ftdi_class.ListDevices()

print(list_of_devices)
for device in list_of_devices:    
  print('\nDetected Instruments:-')
  print(f'\nDevice Name: {device.Description},  Serial Number: {device.SerialNumber}')

TSL550_Laser = ftdi.FTD2xx_helper("19100002")
TSL550_Laser.Write("SO")#Open Shutter
