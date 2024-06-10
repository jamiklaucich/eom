import os
import sys
import time
import clr
import pyvisa as visa
import pandas as pd
import numpy as np

def device_connect(laser_add="19100002", osa_add="ASRL5::INSTR"):
    assembly_path = r"C:/Users/qv18366/OneDrive - University of Bristol/Desktop/Santec/DLL"  # device-class path
    sys.path.append(assembly_path)
    ref = clr.AddReference(r"Santec_FTDI")
    import Santec_FTDI as ftdi# Importing the main method from the DLL
    # Calling the FTD2xx_helper class from the Santec_FTDI dll
    ftdi_class = ftdi.FTD2xx_helper
    laser = ftdi.FTD2xx_helper(laser_add)

    rm = visa.ResourceManager()
    osa = rm.open_resource(osa_add,
                            write_termination = '\n',
                            read_termination = '\n')
    osa.timeout=2000

    return laser, osa

def osa_init(osa):
    osa.write("*RST")
    time.sleep(50)
    osa.write("*IDN?")
    osa.write("BUZ OFF")
    osa.write("EMK")

def osa_wait(osa,command, repeat_time=2):
    comp=0
    time.sleep(repeat_time)
    while not comp:
        osa.write(command)
        comp=int(osa.read())
    return(comp)

def wavelength_calibration(osa, laser, pow_cal=False, l_wait=0.5, o_wait=2, wl_span=2):
    calib_wl=1550#nm
    opow=1#mW
    wl_off=0
    wl_off_ext=0
    laser.Write(f"LP{opow}")
    laser.write(f"WA {calib_wl}")
    laser.Write("SO")
    osa.write(f"CNT {calib_wl}")
    osa.write(f"SPN {wl_span}")
    time.sleep(l_wait)
    osa.write("SSI")
    sweep_done = osa_wait(osa, "ESR2?", o_wait)
    osa.write("PKS PEAK")
    peak_done = osa_wait(osa, "ESR2?", o_wait)
    osa.write("TMK?")
    sweep_res=osa.read().split(",")
    wl_osa=float(sweep_res[0])
    pow_osa=float(sweep_res[1][:-4])
    wl_off=calib_wl-wl_osa
    if(wl_off>1):
        wl_off_ext=wl_off-1
        wl_off=1
    
    osa.write(f"WOFS {wl_off}")
    if(pow_cal):
        pow_off=10*np.log10(opow)-pow_osa
        osa.write(f"LOFS {pow_off}")
        return wl_off, wl_off_ext, pow_off

    return wl_off, wl_off_ext
    