from Behavior import *
import numpy as np

class Response:
    """ this class handles the response to the licks
    """
    def __init__(self, logger, timer, params):
        self.logger = logger
        self.air_dur = params['airpuff_duration']
        self.timer = timer
        self.reward_probe = []

        # calculate pulse duration for the desired reward amount
        self.liquid_dur = dict()
        probes = (LiquidCalibration() & dict(setup=self.logger.setup)).fetch['probe']
        for probe in list(set(probes)):
            key = dict(setup=self.logger.setup, probe=probe)
            dates = (LiquidCalibration() & key).fetch.order_by('date')['date']
            key['date'] = dates[-1]  # use the most recent calibration
            pulse_dur, pulse_num, weight = (LiquidCalibration.PulseWeight() & key).fetch['pulse_dur',
                                                                                         'pulse_num',
                                                                                         'weight']
            self.liquid_dur[probe] = np.interp(params['reward_amount'],
                                               weight/pulse_num,
                                               pulse_dur)

    def punish(self, probe):
        print('Punishing!')
        self.give_air(probe, self.air_dur)
        self.logger.log_air()

    def reward(self, probe):
        print('Rewarding!')
        self.give_liquid(probe, self.liquid_dur[probe])
        self.logger.log_reward()

    def give_air(self, probe, duration):
        pass

    def give_liquid(self, probe, duration):
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


class MultiProbeResponse(Response):

    def prepare_response(self, cond):
        self.reward_probe = (RewardCond() & self.logger.session_key & dict(cond_idx=cond)).fetch1['probe']

    def trial_lick(self, probe):
        if self.reward_probe == probe:
            self.reward(probe)
        else:
            self.punish(probe)

        return True  # break trial

    def trial_no_lick(self):
        if self.reward_probe == 0:
            print('correct!')
        else:
            print('wrong!')

    def inter_trial_lick(self, probe):
        print('wait!')
        self.timer.start()


class FreeWater(Response):
    def trial_lick(self, probe):
        self.reward(probe)


class Calibrator(Response):
    def __init__(self):
        pass

