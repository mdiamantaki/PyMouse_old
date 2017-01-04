from Behavior import *
import numpy as np
import time, pygame, importlib
from Timer import *

# setup GPIO if exists
if importlib.util.find_spec('RPi'):
    from RPi import GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setup([2, 9], GPIO.IN)
    GPIO.setup([3, 4, 10, 11], GPIO.OUT)
    channels = {'air':    {1: 10, 2: 11},
                'liquid': {1: 3,  2: 4},
                'lick':   {1: 2,  2: 9}}


class Licker:
    """ this class handles the licks
    """
    def __init__(self, logger, resp_int):
        self.logger = logger
        self.resp_ind = resp_int
        self.timer = Timer()
        self.timer.start()

    def lick(self):
        probe = 0

        events = pygame.event.get()

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.logger.log_lick()
                    if self.timer.elapsed_time() > self.resp_ind:
                        self.timer.start()
                        probe = 1
                elif event.key == pygame.K_RIGHT:
                    self.logger.log_lick()
                    if self.timer.elapsed_time() > self.resp_ind:
                        self.timer.start()
                        probe = 2

        return probe

    def minutessincelastlick(self):
        return self.timer.elapsed_time()/1000/60


class Response:
    """ this class handles the response to the licks
    """
    def __init__(self, logger, timer, params):
        self.logger = logger
        self.air_dur = params['airpuff_duration']
        self.timeout = params['timeout_duration']
        self.timer = timer
        self.reward_probe = []
        self.__calc_pulse_dur(params['reward_amount'])

    def punish(self, probe):
        pass

    def reward(self, probe):
        pass

    def prepare_response(self, cond):
        pass

    def trial_lick(self, probe):
        return True  # break trial

    def trial_no_lick(self):
        pass

    def inter_trial_lick(self, probe):
        pass

    def inter_trial_no_lick(self):
        pass

    def _pulse_out(self):
        pass

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
            self.liquid_dur[probe] = np.interp(reward_amount,
                                               weight/pulse_num,
                                               pulse_dur)


class RPResponse(Response):
    def __init__(self, logger, timer, params):
        super().__init__(logger, timer, params)

    def prepare_response(self, cond):
        self.reward_probe = (RewardCond() & self.logger.session_key & dict(cond_idx=cond)).fetch1['probe']

    def trial_lick(self, probe):
        if self.reward_probe == probe:
            self.reward(probe)
        else:
            self.punish(probe)
        return True  # break trial

    def inter_trial_lick(self, probe):
        print('wait!')
        self.timer.start()
        self.timer.add_delay(self.timeout)

    def punish(self, probe):
        self._pulse_out(channels['air'][probe], self.air_dur)
        self.logger.log_air()

    def reward(self, probe):
        self._pulse_out(channels['liquid'][probe], self.liquid_dur[probe])
        self.logger.log_reward()

    def _pulse_out(self, channel, duration):
        GPIO.output(channel, GPIO.HIGH)
        time.sleep(duration/1000)
        GPIO.output(channel, GPIO.LOW)


class MultiProbeResponse(Response):
    def prepare_response(self, cond):
        self.reward_probe = (RewardCond() & self.logger.session_key & dict(cond_idx=cond)).fetch1['probe']

    def trial_lick(self, probe):
        if self.reward_probe == probe:
            self.reward(probe)
        else:
            self.punish(probe)
        return True  # break trial

    def punish(self, probe):
        print('Punishing!')
        self.logger.log_air()

    def reward(self, probe):
        print('Rewarding!')
        self.logger.log_reward()

    def inter_trial_lick(self, probe):
        print('wait!')
        self.timer.start()
        self.timer.add_delay(self.timeout)


class FreeWater(Response):
    def trial_lick(self, probe):
        self.reward(probe)


class Calibrator(Response):
    def __init__(self):
        pass

    def reward(self, probe, duration):
        pass


