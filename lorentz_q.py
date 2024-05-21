import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from tkinter import Tk, filedialog

# Function to prompt the user to select a CSV file
def select_file():
    root = Tk()
    root.withdraw()  # Hide the root window
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    return file_path

# Define the Lorentzian function
def lorentzian(wavelength, w0, gamma, A, y0):
    return A / ((wavelength - w0)**2 + (gamma / 2)**2) + y0

# Prompt the user to select a CSV file
file_path = select_file()
if not file_path:
    print("No file selected.")
    exit()

# Read the selected CSV file
print(file_path)
data = pd.read_csv(file_path)
wavelength = data.iloc[:, 0].values
power = data.iloc[:, 1].values

# Find the initial guess for the Lorentzian parameters
min_power = np.min(power)
min_index = np.argmin(power)
w0_initial = wavelength[min_index]
y0_initial = np.mean(power[:10])  # average of the first 10 points as baseline
A_initial = min_power - y0_initial
gamma_initial = (wavelength[-1] - wavelength[0]) / 10  # initial guess for FWHM

initial_guess = [w0_initial, gamma_initial, A_initial, y0_initial]

# Fit the Lorentzian function to the data
popt, pcov = curve_fit(lorentzian, wavelength, power, p0=initial_guess)

# Extract the fitted parameters
w0_fit, gamma_fit, A_fit, y0_fit = popt

# Calculate the Q-factor
fwhm = gamma_fit
Q_factor = w0_fit / fwhm

print(f'Resonant wavelength (w0): {w0_fit}')
print(f'Full Width at Half Maximum (FWHM): {fwhm}')
print(f'Q-factor: {Q_factor}')

# Plot the data and the fit
plt.plot(wavelength, power, 'b-', label='data')
plt.plot(wavelength, lorentzian(wavelength, *popt), 'r--', label='fit')
plt.xlabel('Wavelength (nm)')
plt.ylabel('Optical Power (dB)')
plt.legend()
plt.title(f'Q-factor = {Q_factor:.2f}')
plt.show()

