from Database import *
from time import sleep
import numpy, socket
from Timer import *
from concurrent.futures import ThreadPoolExecutor
from importlib import util
import serial
import sys
import threading

class Probe:
    def __init__(self, logger):
        self.logger = logger
        self.probe1 = False
        self.probe2 = False
        self.ready = False
        self.timer_probe1 = Timer()
        self.timer_probe2 = Timer()
        self.timer_ready = Timer()

    def give_air(self, probe, duration, log=True):
        self.thread.submit(self.__pulse_out, self.channels['air'][probe], duration)
        if log:
            self.logger.log_air(probe)

    def give_liquid(self, probe, duration=False, log=True):
        if not duration:
            duration = self.liquid_dur[probe]
        self.thread.submit(self.__pulse_out, self.channels['liquid'][probe], duration)
        if log:
            self.logger.log_liquid(probe)

    def give_odor(self, odor_idx, duration, log=True):
        print('Odor %1d presentation for %d' % (odor_idx, duration))
        self.thread.submit(self.__pulse_out, self.channels['odor'][odor_idx], duration)
        if log:
            self.logger.log_odor(odor_idx)

    def lick(self):
        if self.probe1:
            self.probe1 = False
            probe = 1
            print('Probe 1 activated')
        elif self.probe2:
            self.probe2 = False
            probe = 2
            print('Probe 2 activated')
        else:
            probe = 0
        return probe

    def probe1_licked(self, channel):
        self.probe1 = True
        self.timer_probe1.start()
        self.logger.log_lick(1)

    def probe2_licked(self, channel):
        self.probe2 = True
        self.timer_probe2.start()
        self.logger.log_lick(2)


    def position_change(self, channel):
        if self.get_input(channel):
            self.timer_ready.start()
            self.ready = True
            print('in position')
        else:
            self.ready = False
            print('off position')

    def in_position(self):
        # handle missed events
        ready = self.get_input(self.channels['start'][1])
        if self.ready != ready:
            self.position_change(self.channels['start'][1])

        return self.ready, self.timer_ready.elapsed_time()

    def get_input(self, channel):
        return True

    def __pulse_out(self, channel, duration):
        pass

    def __calc_pulse_dur(self, reward_amount):  # calculate pulse duration for the desired reward amount
        self.liquid_dur = dict()
        probes = (LiquidCalibration() & dict(setup=self.logger.setup)).fetch['probe']
        for probe in list(set(probes)):
            key = dict(setup=self.logger.setup, probe=probe)
            dates = (LiquidCalibration() & key).fetch('date', order_by='date')
            key['date'] = dates[-1]  # use the most recent calibration
            pulse_dur, pulse_num, weight = (LiquidCalibration.PulseWeight() & key).fetch['pulse_dur',
                                                                                         'pulse_num',
                                                                                         'weight']
            self.liquid_dur[probe] = numpy.interp(reward_amount,
                                                  numpy.divide(weight, pulse_num),
                                                  pulse_dur)

    def cleanup(self):
        pass

class RPProbe(Probe):
    def __init__(self, logger):
        super(RPProbe, self).__init__(logger)
        from RPi import GPIO
        setup = int(''.join(list(filter(str.isdigit, socket.gethostname()))))
        GPIO.setmode(GPIO.BCM)
        GPIO.setup([17, 27, 9], GPIO.IN)
        GPIO.setup([22, 23, 24, 25], GPIO.OUT, initial=GPIO.LOW)
        self.channels = {'odor': {1: 24, 2: 25},
                    'liquid': {1: 22, 2: 23},
                    'lick': {1: 17, 2: 27},
                    'start': {1: 9}}  # 2
        GPIO.add_event_detect(self.channels['lick'][2], GPIO.RISING, callback=self.probe2_licked, bouncetime=200)
        GPIO.add_event_detect(self.channels['lick'][1], GPIO.RISING, callback=self.probe1_licked, bouncetime=200)
        if 3000 < setup < 3100:
            GPIO.add_event_detect(self.channels['start'][1], GPIO.BOTH, callback=self.position_change)

    def get_input(self, channel):
        return GPIO.input(channel)

    def __pulse_out(self, channel, duration):
        GPIO.output(channel, GPIO.HIGH)
        sleep(duration/1000)
        GPIO.output(channel, GPIO.LOW)

    def cleanup(self):
        GPIO.remove_event_detect(self.channels['lick'][1])
        GPIO.remove_event_detect(self.channels['lick'][2])
        if 3000 < setup < 3100:
            GPIO.remove_event_detect(self.channels['start'][1])
        GPIO.cleanup()


class SerialProbe:
    def __init__(self, logger):
        self.port = serial.serial_for_url('/dev/cu.UC-232AC')
        super(RPProbe, self).__init__(logger)

    class GetHWPoller(threading.Thread):
        """ thread to repeatedly poll hardware
        sleeptime: time to sleep between pollfunc calls
        pollfunc: function to repeatedly call to poll hardware"""

        def __init__(self, sleeptime, pollfunc):

            self.sleeptime = sleeptime
            self.pollfunc = pollfunc
            threading.Thread.__init__(self)
            self.runflag = threading.Event()  # clear this to pause thread
            self.runflag.clear()

        def run(self):
            self.runflag.set()
            self.worker()

        def worker(self):
            while True:
                if self.runflag.is_set():
                    self.pollfunc()
                    time.sleep(self.sleeptime)
                else:
                    time.sleep(0.01)

        def pause(self):
            self.runflag.clear()

        def resume(self):
            self.runflag.set()

        def running(self):
            return (self.runflag.is_set())

        def kill(self):
            print("WORKER END")
            sys.stdout.flush()
            self._Thread__stop()