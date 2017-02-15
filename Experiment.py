from Behavior import *
import time


class Experiment:
    """ this class handles the response to the licks
    """
    def __init__(self, logger, timer, params):
        self.logger = logger
        self.air_dur = params['airpuff_duration']
        self.timeout = params['timeout_duration']
        self.silence = params['silence_thr']
        self.timer = timer
        self.reward_probe = []
        self.beh = self.get_behavior()(logger, params)

    def pre_trial(self, cond):
        """Prepare things before trial starts"""
        pass

    def trial(self):
        """Do stuff in trial, returns break condition"""
        return False

    def post_trial(self, trial_broke=False):
        """Handle events after trial ends"""
        pass

    def inter_trial(self):
        """Handle intertrial period events"""
        pass

    def punish(self, probe):
        pass

    def reward(self, probe):
        pass

    def get_behavior(self):
        return RPBehavior

class MultiProbe(Experiment):
    """2AFC & GoNOGo tasks with lickspout"""

    def __init__(self, logger, timer, params):
        self.post_wait = 0
        super(MultiProbe, self).__init__(logger, timer, params)

    def pre_trial(self, cond):
        self.reward_probe = (RewardCond() & self.logger.session_key & dict(cond_idx=cond)).fetch1['probe']

    def trial(self):
        probe = self.beh.is_licking()
        if probe > 0:
            if self.reward_probe == probe:
                self.reward(probe)
            else:
                self.punish(probe)
            return True  # break trial
        else:
            return False

    def post_trial(self, trial_broke):
        time.sleep(self.post_wait)
        self.post_wait = 0

    def inter_trial(self):
        if self.beh.is_licking():
            self.timer.start()
        elif self.beh.inactivity_time() > self.silence:
            self.logger.update_setup_state('sleeping')
            while not self.beh.is_licking() and self.logger.get_setup_state() == 'sleeping':
                time.sleep(1)
            self.logger.update_setup_state('running')

    def punish(self, probe):
        self.beh.punish_with_air(probe, self.air_dur)
        self.post_wait = self.timeout

    def reward(self, probe):
        self.beh.water_reward(probe)


class DummyMultiProbe(MultiProbe):
    """Testing"""

    def get_behavior(self):
        return DummyProbe


class FreeWater(Experiment):
    """Reward upon lick"""
    def trial(self):
        probe = self.beh.is_licking()
        if probe:
            self.beh.water_reward(probe)


class ProbeTest(Experiment):
    """Reward upon lick"""
    def trial(self):
        probe = self.beh.is_licking()
        if probe:
            self.beh.water_reward(probe)
            self.beh.punish_with_air(probe)


