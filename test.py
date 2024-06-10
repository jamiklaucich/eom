import os
import clr
import sys
import time
import pyvisa as visa
import numpy as np
from utilities.ThorlabsPM100.ThorlabsPM100 import *
import serial

data = '1530.54,-40.45DBM\r'
data_=data.split(",")[0][:-4]
print(data_)