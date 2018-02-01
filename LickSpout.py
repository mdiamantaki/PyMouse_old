from Database import *
from time import sleep
import numpy, socket
from Timer import *
from concurrent.futures import ThreadPoolExecutor
from importlib import util
from ThreadWorker import GetHWPoller
import serial
import sys
import platform


class Probe:
    def __init__(self, logger):
        self.logger = logger
        self.probe1 = False
        self.probe2 = False
        self.ready = False
        self.timer_probe1 = Timer()
        self.timer_probe2 = Timer()
        self.timer_ready = Timer()
        self.__calc_pulse_dur(logger.reward_amount)
        self.thread = ThreadPoolExecutor(max_workers=1)

    def give_air(self, probe, duration, log=True):
        pass

    def give_liquid(self, probe, duration=False, log=True):
        pass

    def give_odor(self, odor_idx, duration, log=True):
        pass

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

    def in_position(self):
        return True, 0

    def __calc_pulse_dur(self, reward_amount):  # calculate pulse duration for the desired reward amount
        self.liquid_dur = dict()
        probes = (LiquidCalibration() & dict(setup=self.logger.setup)).fetch('probe')
        for probe in list(set(probes)):
            key = dict(setup=self.logger.setup, probe=probe)
            dates = (LiquidCalibration() & key).fetch('date', order_by='date')
            key['date'] = dates[-1]  # use the most recent calibration
            pulse_dur, pulse_num, weight = (LiquidCalibration.PulseWeight() & key).fetch('pulse_dur',
                                                                                         'pulse_num',
                                                                                         'weight')
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
        self.channels = {'air': {1: 24, 2: 25},
                    'liquid': {1: 22, 2: 23},
                    'lick': {1: 17, 2: 27},
                    'start': {1: 9}}  # 2
        GPIO.add_event_detect(self.channels['lick'][2], GPIO.RISING, callback=self.probe2_licked, bouncetime=200)
        GPIO.add_event_detect(self.channels['lick'][1], GPIO.RISING, callback=self.probe1_licked, bouncetime=200)
        if 3000 < setup < 3100:
            GPIO.add_event_detect(self.channels['start'][1], GPIO.BOTH, callback=self.position_change)

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
        self.thread.submit(self.__pulse_out, self.channels['air'][odor_idx], duration)
        if log:
            self.logger.log_odor(odor_idx)

    def position_change(self, channel):
        if self.self.is_ready():
            self.timer_ready.start()
            self.ready = True
            print('in position')
        else:
            self.ready = False
            print('off position')

    def in_position(self):
        # handle missed events
        ready = GPIO.input(self.channels['start'][1])
        if self.ready != ready:
            self.position_change()
        return self.ready, self.timer_ready.elapsed_time()

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


class SerialProbe(Probe):
    def __init__(self, logger):
        if platform.system() == 'linux':
            ser_port = '/dev/ttyUSB0'
        else:
            ser_port = '/dev/cu.UC-232AC'
        self.serial = serial.serial_for_url(ser_port)
        self.serial.dtr = False
        self.serial.rts = False
        super(SerialProbe, self).__init__(logger)
        self.worker = GetHWPoller(0.001, self.poll_probe)
        self.interlock = False  # set to prohibit thread from accessing serial port
        self.worker.start()

    def give_liquid(self, probe, duration=False, log=True):
        if not duration:
            duration = self.liquid_dur[probe]
        self.thread.submit(self.__pulse_out, duration)
        if log:
            self.logger.log_liquid(probe)

    def poll_probe(self):
        if self.interlock:
            return "interlock"  # someone else is using serial port, wait till done!
        self.interlock = True  # set interlock so we won't be interrupted
        response1 = self.serial.dsr  # read a byte from the hardware
        response2 = self.serial.cts  # read a byte from the hardware
        self.interlock = False
        if response1:
            if self.timer_probe1.elapsed_time() > 200:
                self.probe1_licked(1)
        if response2:
            if self.timer_probe2.elapsed_time() > 200:
                self.probe2_licked(2)

    def __pulse_out(self, probe, duration):
        while self.interlock:  # busy, wait for free, should timeout here
            print("waiting for interlock")
            sys.stdout.flush()
        self.interlock = True
        if probe == 1:
            self.serial.dtr = True
            sleep(duration/1000)
            self.serial.dtr = False
        elif probe == 2:
            self.serial.rts = True
            sleep(duration/1000)
            self.serial.rts = False
        self.interlock = False

    def cleanup(self):
        self.worker.kill()


