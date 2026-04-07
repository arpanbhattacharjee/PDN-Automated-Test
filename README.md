# PDN Load Transient Automated Test

## Overview
This repository contains a Python-based Automated Test Equipment (ATE) script designed to execute load transient testing on a 4-rail Power Distribution Network (PDN) for a satellite payload. 

Using SCPI commands via PyVISA, the script fully automates the initialization of lab instruments, executes a continuous load transient sequence, captures oscilloscope waveforms over USB, and logs peak-to-peak voltage ripple to generate a final CSV compliance report.

## Hardware Requirements
This script is configured for the following specific lab instrumentation:
* **DC Power Supply:** Keithley 2230-30-1 (Input Power)
* **Programmable Electronic Load:** Keithley 2380 Series (Transient Sinking)
* **Oscilloscope:** Keysight DSOX6004A (Measurement & Waveform Capture)

## Software Requirements
* Python 3.8+
* [PyVISA](https://pyvisa.readthedocs.io/)
* NI-VISA or Keysight IO Libraries Suite (for USB/GPIB instrument drivers)

## Installation
1. Clone the repository:
   ```bash
   git clone [https://github.com/yourusername/PDN-Automated-Test.git](https://github.com/arpanbhattacharjee/PDN-Automated-Test.git)
