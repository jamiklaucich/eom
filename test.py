import os
import clr
import sys
import time
import pyvisa as visa

rm = visa.ResourceManager()
rm.list_resources()
keithley_2450 = rm.open_resource("USB0::0x05E6::0x2450::04610529::0::INSTR")