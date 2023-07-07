# this file runs the open loop data collection experiments for the APPJ testbed
# in the following paper:
#
#
# Requirements:
# * Python 3
# * several 3rd party packages including CasADi, NumPy, Scikit-Optimize for
# the implemented algorithms and Seabreeze, os, serial, etc. for connection to
# the experimental setup.
#
# Copyright (c) 2021 Mesbah Lab. All Rights Reserved.
# Contributor(s): Kimberly Chan
# Affiliation: University of California, Berkeley
#
# This file is under the MIT License. A copy of this license is included in the
# download of the entire code package (within the root folder of the package).

## import 3rd party packages
import sys
sys.dont_write_bytecode = True
import numpy as np
from seabreeze.spectrometers import Spectrometer, list_devices
import time
import os
import serial
import cv2
from datetime import datetime
import asyncio
from datetime import datetime
import pandas as pd
from picosdk.ps2000a import ps2000a as ps
import matplotlib.pyplot as plt

# pickle import to save class data
try:
    import cPickle as pickle
except ModuleNotFoundError:
    import pickle
import argparse

## import user functions
import utils.APPJPythonFunctions as appj
from utils.experiments import Experiment
from utils.oscilloscope import Oscilloscope 

TEST = False       #for testing the code without any devices connected

plot_data = True # [True/False] whether or not to plot the (2-input, 2-output) data after an experiment

sample_num_default = 0      # sample number for treatment
time_treat_default = 30.0   # time to run experiment in seconds
P_treat_default = 2.0       # power setting for the treatment in Watts
q_treat_default = 2.0       # flow setting for the treatment in standard liters per minute (SLM)
dist_treat_default = 4.0    # jet-to-substrate distance in mm
int_time_default = 12000*6  # integration time for spectrometer measurement in microseconds
ts_default = 1.0            # sampling time to take measurements in seconds
# NOTE: sampling time should be greater than integration time by roughly double

################################################################################
# USER OPTIONS (you may change these)
################################################################################
# variables that WILL change the function of the data collection
save_backup = True          # whether [True] or not [False] to save a compressed H5 backup file every 10 iterations
async_collection = True     # whether [True] or not [False] to collect data asynchronously, if this is True, then collect_osc and collect_spec will be automatically set to True regardless of the settings in the following two lines
collect_spec = True         # whether [True] or not [False] to collect data from the spectrometer
collect_osc = True          # whether [True] or not [False] to collect data from the oscilloscope
collect_tc = True           # whether [True] or not [False] to collect data from the Thermal Camera
samplingTime = 0.5          # sampling time in seconds
# n_iterations = input("Number of iterations?:") # number of sampling iterations
n_iterations = 101


# variables that will NOT change the function of the data collection (for note-taking purposes)
DEFAULT_EMAIL = "kchan45@berkeley.edu"          # the default email address to send the data to
set_v = 85.0             # voltage in Volts
set_freq = 200.0        # frequency in hertz
set_flow = 0.5          # flow rate in liters per minute
set_gap = 5.0           # distance reactor to target in mm
set_target = input("Target?:")
addl_notes = "chicken I"

plot_last_data = True       # whether [True] or not [False] to plot the data from the final iteration of the data collection

## OPTIONAL Configurations for the spectrometer - in case the settings for the spectrometer need to be customized
integration_time = 200000       # in microseconds

## OPTIONAL Configurations for the oscilloscope - in case the settings for the oscilloscope need to be customized
mode = 'block'  # use block mode to capture the data using a trigger; the other option is 'streaming'
# for block mode, you may wish to change the following:
pretrigger_size = 200      # size of the data buffer before the trigger, default is 2000, in units of samples
posttrigger_size = 800     # size of the data buffer after the trigger, default is 8000, in units of samples
# for streaming mode, you may wish to change the following:
single_buffer_size = 500    # size of
n_buffers = 10              # number of buffers to acquire, default is 10
timebase = 2              # timebase for the measurement resolution, 127 corresponds to 1us, default is 8

# see oscilloscope_test.py for more information on defining the channels
channelA = {"name": "A",
            "enable_status": 1,
            "coupling_type": ps.PS2000A_COUPLING['PS2000A_DC'],
            "range": ps.PS2000A_RANGE['PS2000A_10V'],
            "analog_offset": 0.0,
            }
channelB = {"name": "B",
            "enable_status": 1,
            "coupling_type": ps.PS2000A_COUPLING['PS2000A_DC'],
            "range": ps.PS2000A_RANGE['PS2000A_20V'],
            "analog_offset": 0.0,
            }
channelC = {"name": "C",
            "enable_status": 1,
            "coupling_type": ps.PS2000A_COUPLING['PS2000A_DC'],
            "range": ps.PS2000A_RANGE['PS2000A_20V'],
            "analog_offset": 0.0,
            }
channelD = {"name": "D",
            "enable_status": 0,
            "coupling_type": ps.PS2000A_COUPLING['PS2000A_DC'],
            "range": ps.PS2000A_RANGE['PS2000A_5V'],
            "analog_offset": 0.0,
            }
# put all desired channels into a list (vector with square brackets) named 'channels'
channels = [channelA, channelB, channelC]
# see oscilloscope_test.py for more information on defining the buffers
# a buffer must be defined for every channel that is defined above
bufferA = {"name": "A",
           "segment_index": 0,
           "ratio_mode": ps.PS2000A_RATIO_MODE['PS2000A_RATIO_MODE_NONE'],
           }
bufferB = {"name": "B"}
bufferC = {"name": "C"}
bufferD = {"name": "D"}
# put all buffers into a list (vector with square brackets) named 'buffers'
buffers = [bufferA, bufferB, bufferC]

# see /test/oscilloscope_test.py for more information on defining the trigger (TODO)
# a trigger is defined to capture the specific pulse characteristics of the plasma
trigger = {"enable_status": 1,
           "source": ps.PS2000A_CHANNEL['PS2000A_CHANNEL_A'],
           "threshold": 1024, # in ADC counts
           "direction": ps.PS2000A_THRESHOLD_DIRECTION['PS2000A_RISING'],
           "delay": 0, # in seconds
           "auto_trigger": 200} # in milliseconds

################################################################################
## Set up argument parser
################################################################################
parser = argparse.ArgumentParser(description='Experiment Settings')
parser.add_argument('-n', '--sample_num', type=int, default=sample_num_default,
                    help='The sample number for the test treatments.')
parser.add_argument('-t', '--time_treat', type=float, default=time_treat_default,
                    help='The treatment time desired in seconds.')
parser.add_argument('-p', '--P_treat', type=float, default=P_treat_default,
                    help='The power setting for the treatment in Watts.')
parser.add_argument('-q', '--q_treat', type=float, default=q_treat_default,
                    help='The flow rate setting for the treatment in SLM.')
parser.add_argument('-d', '--dist_treat', type=float, default=dist_treat_default,
                    help='The jet-to-substrate distance in millimeters.')
parser.add_argument('-it', '--int_time_treat', type=float, default=int_time_default,
                    help='The integration time for the spectrometer in microseconds.')
parser.add_argument('-ts', '--sampling_time', type=float, default=ts_default,
                    help='The sampling time to take measurements in seconds.')

args = parser.parse_args()
sample_num = args.sample_num
time_treat = args.time_treat
P_treat = args.P_treat
q_treat = args.q_treat
dist_treat = args.dist_treat
int_time_treat = args.int_time_treat
ts = args.sampling_time

settings_str = f"The settings for this treatment are:\n"\
      f"Sample Number:              {sample_num}\n"\
      f"Treatment Time (s):         {time_treat}\n"\
      f"Power (W):                  {P_treat}\n"\
      f"Flow Rate (SLM):            {q_treat}\n"\
      f"Separation Distance (mm):   {dist_treat}\n"\
      f"Integration Time (us):      {int_time_treat}\n"\
      f"Sampling Time (s):          {ts}\n"
print(settings_str)

if ts < 2*int_time_treat*1e-6:
    print("Integration time too large! Please modify the integration time and/or the sampling time such that the sampling time is greater than double the integration time.")
    exit(1)

cfm = input("Confirm these are correct: [Y/n]\n")
if cfm in ['Y', 'y']:
    pass
else:
    quit()

################################################################################
## Startup/prepare APPJ
################################################################################

## collect time stamp
timeStamp = datetime.now().strftime('%Y_%m_%d_%H'+'h%M''m%S'+'s')
print('Timestamp for save files: ', timeStamp)
Nrep = 1

# configure run options
runOpts = appj.RunOpts()
runOpts.collectData = True      # option to collect two-input, two-output data (power, flow rate); (max surface temperature, total intensity)
runOpts.collectEntireSpectra = True # option to collect full intensity spectra
runOpts.collectOscMeas = False # option to collect oscilloscope measurements (not functioning)
runOpts.collectSpatialTemp = False # option to collect spatial temperature (defined as temperature from 12 pixels away from max in the four cardinal directions)
# save options; correspond to the collection (two-input, two-output data is always saved)
runOpts.saveSpectra = True
runOpts.saveOscMeas = False
runOpts.saveSpatialTemp = False # limited functionality
runOpts.saveEntireImage = False # limited/no functionality

runOpts.tSampling = ts # set the sampling time of the measurements

Nsim = int(time_treat/runOpts.tSampling)

## Set startup values
dutyCycleIn = 100
powerIn = P_treat
flowIn = q_treat

# set save location
directory = os.getcwd()
split_cwd = directory.split('/')
repo = split_cwd[-1]
saveDir = directory+f"/../{repo}-ExperimentalData/"+timeStamp+f"-Sample{sample_num}/"
print('\nData will be saved in the following directory:')
print(saveDir)

## connect to/open connection to devices in setup
# Arduino
arduinoAddress = appj.getArduinoAddress(os="ubuntu")
print("Arduino Address: ", arduinoAddress) 
arduinoPI = serial.Serial(arduinoAddress, baudrate=38400, timeout=1)
s = time.time()
# # Oscilloscope
# oscilloscope = appj.Oscilloscope()       # Instantiate object from class
# instr = oscilloscope.initialize(retry=1)	# Initialize oscilloscope

################################################################################
# PREPARE NOTES AND SET UP FILES FOR DATA COLLECTION
# Recommended: Do NOT edit beyond this section
################################################################################
if async_collection:
    collect_osc = True
    collect_spec = True
    collect_tc = True

################################################################################
# CONNECT TO DEVICES
################################################################################
# Spectrometer
if collect_spec:
    if not TEST:
        # for testing this code, it is not required to connect to the device;
        # if you wish to test the connection to the device, please use the spectrometer_test.py
        # this code detects the first available spectrometer connected to the computer
        # devices = list_devices()
        # print(devices)
        # spec = Spectrometer(devices[0])
        spec = Spectrometer.from_first_available()
        spec.integration_time_micros(integration_time)
    else:
        spec = None

# Oscilloscope
if collect_osc:
    if not TEST:
        # for testing this code, it is not required to connect to the device;
        # if you wish to test the connection to the device, please use the oscilloscope_test.py
        osc = Oscilloscope()
        status = osc.open_device()
        status = osc.initialize_device(channels, buffers, trigger=trigger, timebase=timebase)
    else:
        osc = None
# Thermal Camera 
if collect_tc:
    if not TEST:
        # for testing this code, it is not required to connect to the device;
        # if you wish to test the connection to the device, please use the thermal_test.py
        dev, ctx = appj.openThermalCamera()
    print("Devices opened/connected to sucessfully!")

devices = list_devices()
print(devices)
devices = {}
devices['arduinoPI'] = arduinoPI
devices['arduinoAddress'] = arduinoAddress
devices['osc'] = osc
devices['spec'] = spec

# send startup inputs
time.sleep(2)
appj.sendInputsArduino(arduinoPI, powerIn, flowIn, dutyCycleIn, arduinoAddress)
input("Ensure plasma has ignited and press Return to begin.\n")


## Startup asynchronous measurement
time.sleep(2)
appj.sendInputsArduino(arduinoPI, powerIn, flowIn, dutyCycleIn, arduinoAddress)
input("Ensure plasma has ignited and press Return to begin.\n")

## Startup asynchronous measurement
if os.name == 'nt':
    ioloop = asyncio.ProactorEventLoop() # for subprocess' pipes on Windows
    asyncio.set_event_loop(ioloop)
else:
    ioloop = asyncio.get_event_loop()
# run once to initialize measurements
prevTime = (time.time()-s)*1e3
tasks, runTime = ioloop.run_until_complete(appj.async_measure(arduinoPI, prevTime, osc, spec, runOpts))
print('measurement devices ready!')
s = time.time()

prevTime = (time.time()-s)*1e3
# get initial measurements
tasks, runTime = ioloop.run_until_complete(appj.async_measure(arduinoPI, prevTime, osc, spec, runOpts))
if runOpts.collectData:
    thermalCamOut = tasks[0].result()
    Ts0 = thermalCamOut[0]
    specOut = tasks[1].result()
    I0 = specOut[0]
    oscOut = tasks[2].result()
    arduinoOut = tasks[3].result()
    outString = "Measured Outputs: Temperature: %.2f, Intensity: %.2f" % (Ts0, I0)
    print(outString)
else:
    Ts0 = 37
    I0 = 100

s = time.time()
################################################################################
## Begin Experiment:
################################################################################
exp = Experiment(Nsim, saveDir)

f = open(saveDir+"notes.txt", 'a')
f.write(settings_str)

for i in range(Nrep):
    s = time.time()

    # create input sequences
    pseq = P_treat*np.ones((Nsim,))
    qseq = q_treat*np.ones((Nsim,))
    print(pseq)
    print(qseq)

    # additional information to save
    opt_dict = {}
    opt_dict['sep_dist'] = dist_treat
    opt_dict['sample_num'] = sample_num

    exp_data = exp.run_open_loop(ioloop,
                                 power_seq=pseq,
                                 flow_seq=qseq,
                                 runOpts=runOpts,
                                 devices=devices,
                                 prevTime=prevTime,
                                 opt_dict=opt_dict)

    arduinoPI.close()

# reconnect Arduino
arduinoPI = serial.Serial(arduinoAddress, baudrate=38400, timeout=1)
devices['arduinoPI'] = arduinoPI

# turn off plasma jet (programmatically)
appj.sendInputsArduino(arduinoPI, 0.0, 0.0, dutyCycleIn, arduinoAddress)
arduinoPI.close()

if plot_data:
    import matplotlib.pyplot as plt
    fig, (ax1, ax2, ax3, ax4) = plt.subplots(4,1, figsize=(8,8), dpi=150)
    ax1.plot(exp_data['Tsave'])
    ax1.set_ylabel('Maximum Surface\nTemperature ($^\circ$C)')
    ax2.plot(exp_data['Isave'])
    ax2.set_ylabel('Total Optical\nEmission Intensity\n(arb. units)')
    ax3.plot(exp_data['Psave'])
    ax3.set_ylabel('Power (W)')
    ax4.plot(exp_data['qSave'])
    ax4.set_ylabel('Carrier Gas\nFlow Rate (SLM)')
    ax4.set_xlabel('Time Step')
    plt.tight_layout()
    plt.show()
    
print("Experiment complete!\n"+
    "################################################################################################################\n"+
    "IF FINISHED WITH EXPERIMENTS, PLEASE FOLLOW THE SHUT-OFF PROCEDURE FOR THE APPJ\n"+
    "################################################################################################################\n")