import os
import clr
import sys
import time
import pyvisa as visa
import numpy as np
from utilities.ThorlabsPM100.ThorlabsPM100 import *
import serial

def osa_wait(command):
    comp=0
    while not comp:
        osa.write(command)
        comp=int(osa.read())
    return(comp)

def osa_init():
    osa.write("*IDN?")
    osa.write("BUZ OFF")

rm = visa.ResourceManager()
print(rm.list_resources())
osa = rm.open_resource('ASRL5::INSTR',
                           write_termination = '\n',
                           read_termination = '\n')
osa.timeout=2000

# osa.write("*RST")

osa_init()
#print(osa.read())
#osa.write("PWR 1550")

osa.write("EMK")
osa.write("SSI")
sweep_done = osa_wait("ESR2?")

print("done")
comp=0
#time.sleep(2)
osa.write("PKS PEAK")
peak_done = osa_wait("ESR2?")
osa.write("TMK?")
print(osa.read())

