from Logger import *
from Stimulus import *
import sys
import time
import numpy as np


# Inputs: duration, probe, pulsenum, pulse_interval
def runner(args):

    duration = int(args[0])  # has to be there

    if np.size(args) > 1:
        probe = int(args[1])
    else:
        probe = 1

    if np.size(args) > 2:
        pulsenum = int(args[2])
    else:
        pulsenum = 100

    if np.size(args) > 3:
        pulse_interval = int(args[3])
    else:
        pulse_interval = 100

    # get objects
    logger = Logger()
    resp = Calibrator()

    # RUN
    print('Running calibration')
    trial = 0
    while trial < pulsenum:

        print('Pulse %d/%d' % (trial+1, pulsenum), end="\r", flush=True)

        # trial period
        resp.reward(probe, duration)

        # wait for next pulse
        time.sleep(duration/1000 + pulse_interval/1000)

        trial += 1

    # get weight from user
    total_weight = input('Total liquid weight (gr): ')

    # insert
    logger.log_pulse_weight(duration, probe, pulsenum, float(total_weight))

    # close everything
    quit()


# input parameters: duration, probe, # of pulses, puse interval
runner(sys.argv[1:])
