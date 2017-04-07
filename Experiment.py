from Behavior import *
from Stimulus import *
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
        self.stim = eval(params['stim_type'])(logger)

    def prepare(self):
        """Prepare things before experiment starts"""
        self.stim.setup()
        self.stim.prepare()  # prepare stimulus

    def pre_trial(self):
        """Prepare things before trial starts"""
        self.stim.init_trial()  # initialize stimulus

    def trial(self):
        """Do stuff in trial, returns break condition"""
        self.stim.present_trial()  # Start Stimulus
        return False

    def post_trial(self):
        """Handle events after trial ends"""
        self.stim.stop_trial()  # stop stimulus

    def inter_trial(self):
        """Handle intertrial period events"""
        pass

    def cleanup(self):
        self.beh.cleanup()

    def get_behavior(self):
        return RPBehavior  # default is raspberry pi


class MultiProbe(Experiment):
    """2AFC & GoNOGo tasks with lickspout"""

    def __init__(self, logger, timer, params):
        self.post_wait = 0
        super(MultiProbe, self).__init__(logger, timer, params)

    def pre_trial(self):
        cond = self.stim.init_trial()
        self.reward_probe = (RewardCond() & self.logger.session_key & dict(cond_idx=cond)).fetch1['probe']
        self.beh.is_licking()

    def trial(self):
        self.stim.present_trial()  # Start Stimulus
        probe = self.beh.is_licking()
        if probe > 0:
            if self.reward_probe == probe:
                self.reward(probe)
            else:
                self.punish(probe)
            return True  # break trial
        else:
            return False

    def post_trial(self):
        self.stim.stop_trial()  # stop stimulus when timeout
        self.timer.start()
        while self.timer.elapsed_time() < self.post_wait and self.logger.get_setup_state() == 'running':
            time.sleep(0.5)
        self.post_wait = 0

    def inter_trial(self):
        if self.beh.is_licking():
            self.timer.start()
        elif self.beh.inactivity_time() > self.silence and self.logger.get_setup_state() == 'running':
            self.logger.update_setup_state('sleeping')
            self.stim.unshow([0, 0, 0])
            while not self.beh.is_licking() and self.logger.get_setup_state() == 'sleeping':
                time.sleep(1)
            self.stim.unshow()
            if self.logger.get_setup_state() == 'sleeping':
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
        self.stim.present_trial()  # Start Stimulus
        probe = self.beh.is_licking()
        if probe:
            self.beh.water_reward(probe)


class ProbeTest(Experiment):
    """Reward upon lick"""
    def prepare(self):
        pass
    
    def trial(self):
        probe = self.beh.is_licking()
        if probe:
            print(probe)
            self.beh.water_reward(probe)
            self.beh.punish_with_air(probe)

