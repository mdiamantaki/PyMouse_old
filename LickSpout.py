from Database import *
from time import sleep
import numpy, socket
from Timer import *
from concurrent.futures import ThreadPoolExecutor
from importlib import util


# setup GPIO
if util.find_spec('RPi'):
    from RPi import GPIO
    setup = int(''.join(list(filter(str.isdigit, socket.gethostname()))))
    GPIO.setmode(GPIO.BCM)
    if 0 < setup < 6:
        GPIO.setup([2, 5], GPIO.IN)
        GPIO.setup([3, 4, 6, 7], GPIO.OUT, initial=GPIO.LOW)
        channels = {'air':    {1: 7,  2: 6},
                    'liquid': {1: 4,  2: 3},
                    'lick':   {1: 2,  2: 5}}
    elif 3000 < setup < 3100:
        GPIO.setup([17, 27, 2], GPIO.IN)
        GPIO.setup([22, 23, 24, 25], GPIO.OUT, initial=GPIO.LOW)
        channels = {'odor': {1: 24, 2: 25},
                    'liquid': {1: 22, 2: 23},
                    'lick': {1: 17, 2: 27},
                    'start': {1: 2}}
    else:
        GPIO.setup([17, 27], GPIO.IN)
        GPIO.setup([22, 23, 24, 25], GPIO.OUT, initial=GPIO.LOW)
        channels = {'air':    {1: 24,  2: 25},
                    'liquid': {1: 22,  2: 23},
                    'lick':   {1: 17,  2: 27}}


class Licker:
    """ this class handles the licks
    """
    def __init__(self, logger):
        self.logger = logger
        self.probe1 = False
        self.probe2 = False
        self.timer_probe1 = Timer()
        self.timer_probe1.start()
        self.timer_probe2 = Timer()
        self.timer_probe2.start()
        self.timer_ready = Timer()
        self.timer_ready.start()
        GPIO.add_event_detect(channels['lick'][2], GPIO.RISING, callback=self.probe2_licked, bouncetime=200)
        GPIO.add_event_detect(channels['lick'][1], GPIO.RISING, callback=self.probe1_licked, bouncetime=200)
        if 3000 < setup < 3100:
            GPIO.add_event_detect(channels['start'][1], GPIO.RISING, callback=self.in_position, bouncetime=200)
            GPIO.add_event_detect(channels['start'][1], GPIO.FALLING, callback=self.off_position, bouncetime=200)

    def probe1_licked(self, channel):
        #c = list(channels['lick'].items())
        #probe = c[0][c[1].index(channel)]
        self.probe1 = True
        self.timer_probe1.start()
        self.logger.log_lick(1)

    def probe2_licked(self, channel):
        self.probe2 = True
        self.timer_probe2.start()
        self.logger.log_lick(2)

    def in_position(self, channel):
        self.timer_ready.start()
        self.ready = True

    def off_position(self, channel):
        self.ready = False

    def is_ready(self):
        return self.ready, self.timer_ready

    def lick(self):
        if self.probe1:
            self.probe1 = False
            probe = 1
        elif self.probe2:
            self.probe2 = False
            probe = 2
        else:
            probe = 0
        return probe

    def cleanup(self):
        GPIO.remove_event_detect(channels['lick'][1])
        GPIO.remove_event_detect(channels['lick'][2])


class ValveControl:
    """ This class handles the control of the valves for air & liquid delivery
    """
    def __init__(self, logger):
        self.thread = ThreadPoolExecutor(max_workers=1)
        self.logger = logger
        self.__calc_pulse_dur(logger.reward_amount)

    def give_air(self, probe, duration, log=True):
        self.thread.submit(self.__pulse_out, channels['air'][probe], duration)
        if log:
            self.logger.log_air(probe)

    def give_liquid(self, probe, duration=False, log=True):
        if not duration:
            duration = self.liquid_dur[probe]
        self.thread.submit(self.__pulse_out, channels['liquid'][probe], duration)
        if log:
            self.logger.log_liquid(probe)

    def give_odor(self, odor_idx, duration):
        self.thread.submit(self.__pulse_out, channels['odor'][odor_idx], duration)

    def __calc_pulse_dur(self, reward_amount):  # calculate pulse duration for the desired reward amount
        self.liquid_dur = dict()
        probes = (LiquidCalibration() & dict(setup=self.logger.setup)).fetch['probe']
        for probe in list(set(probes)):
            key = dict(setup=self.logger.setup, probe=probe)
            dates = (LiquidCalibration() & key).fetch.order_by('date')['date']
            key['date'] = dates[-1]  # use the most recent calibration
            pulse_dur, pulse_num, weight = (LiquidCalibration.PulseWeight() & key).fetch['pulse_dur',
                                                                                         'pulse_num',
                                                                                         'weight']
            self.liquid_dur[probe] = numpy.interp(reward_amount,
                                                  numpy.divide(weight, pulse_num),
                                                  pulse_dur)

    def __pulse_out(self, channel, duration):
        GPIO.output(channel, GPIO.HIGH)
        sleep(duration/1000)
        GPIO.output(channel, GPIO.LOW)

