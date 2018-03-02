from Behavior import *
from Stimulus import *
import time, numpy


class Experiment:
    """ this class handles the response to the licks
    """
    def __init__(self, logger, timer, params):
        self.logger = logger
        self.air_dur = params['airpuff_duration']
        self.timeout = params['timeout_duration']
        self.silence = params['silence_thr']
        self.ready_wait = params['init_duration']
        self.randomization = params['randomization']
        self.timer = timer
        self.reward_probe = []
        self.conditions = []
        self.probes = []
        self.post_wait = 0
        self.indexes = []
        self.beh = self.get_behavior()(logger, params)
        self.stim = eval(params['stim_type'])(logger, self.beh)
        self.probe_bias = numpy.repeat(numpy.nan, 1)   # History term for bias calculation

    def prepare(self):
        """Prepare things before experiment starts"""
        self.stim.setup()

    def run(self):
        return self.logger.get_setup_state() == 'running'

    def pre_trial(self):
        """Prepare things before trial starts"""
        self.stim.init_trial()  # initialize stimulus
        self.logger.ping()

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

    def on_hold(self, status=False):
        """Handle events that happen in between experiments"""
        pass

    def cleanup(self):
        self.beh.cleanup()

    def get_behavior(self):
        return RPBehavior  # default is raspberry pi

    def _get_new_cond(self):
        """Get curr condition & create random block of all conditions
        Should be called within init_trial
        """
        if self.randomization == 'block':
            if numpy.size(self.indexes) == 0:
                self.indexes = numpy.random.permutation(numpy.size(self.conditions))
            cond = self.conditions[self.indexes[0]]
            self.indexes = self.indexes[1:]
            return cond
        elif self.randomization == 'random':
            return numpy.random.choice(self.conditions)
        elif self.randomization == 'bias':
            if len(self.probe_bias) == 0 or numpy.all(numpy.isnan(self.probe_bias)):
                self.probe_bias = numpy.random.choice(self.probes, 5)
                return numpy.random.choice(self.conditions)
            else:
                mn = numpy.min(self.probes)
                mx = numpy.max(self.probes)
                bias_probe = numpy.random.binomial(1, 1 - numpy.nanmean((self.probe_bias - mn)/(mx-mn)))*(mx-mn) + mn
                self.probe_bias = np.concatenate((self.probe_bias[1:], [numpy.random.choice(self.probes)]))
                return numpy.random.choice(self.conditions[self.probes == bias_probe])


class MultiProbe(Experiment):
    """2AFC & GoNOGo tasks with lickspout"""

    def __init__(self, logger, timer, params):
        self.post_wait = 0
        self.responded = False
        super(MultiProbe, self).__init__(logger, timer, params)

    def prepare(self):
        self.conditions, self.probes = self.logger.log_conditions(self.stim.get_condition_table())  # log conditions
        self.stim.setup()
        self.stim.prepare(self.conditions)  # prepare stimulus

    def pre_trial(self):
        cond = self._get_new_cond()
        self.stim.init_trial(cond)
        self.reward_probe = (RewardCond() & self.logger.session_key & dict(cond_idx=cond)).fetch1('probe')
        self.beh.is_licking()

    def trial(self):
        self.stim.present_trial()  # Start Stimulus
        probe = self.beh.is_licking()
        if probe > 0 and not self.responded:
            self.responded = True
            self.probe_bias[-1] = probe  # bias correction
            if self.reward_probe == probe:
                print('Correct!')
                self.reward(probe)
                self.timer.start()
                while self.timer.elapsed_time() < 1000:  # give an extra second to associate the reward with stimulus
                    self.stim.present_trial()
                return True
            else:
                print('Wrong!')
                self.punish(probe)
                return True  # break trial
        else:
            return False

    def post_trial(self):
        self.stim.stop_trial()  # stop stimulus when timeout
        self.responded = False
        self.timer.start()
        while self.timer.elapsed_time()/1000 < self.post_wait and self.logger.get_setup_state() == 'running':
            time.sleep(0.5)
        self.post_wait = 0

    def inter_trial(self):
        if self.beh.is_licking():
            self.timer.start()
        elif self.beh.inactivity_time() > self.silence and self.logger.get_setup_state() == 'running':
            self.logger.update_setup_state('sleeping')
            self.stim.unshow([0, 0, 0])
            self.probe_bias = numpy.repeat(numpy.nan, 1)  # reset bias
            while not self.beh.is_licking() and self.logger.get_setup_state() == 'sleeping':
                self.logger.ping()
                time.sleep(1)
            self.stim.unshow()
            if self.logger.get_setup_state() == 'sleeping':
                self.logger.update_setup_state('running')
                self.timer.start()

    def punish(self, probe):
        self.beh.punish_with_air(probe, self.air_dur)
        self.post_wait = self.timeout

    def reward(self, probe):
        self.beh.water_reward(probe)


class DummyMultiProbe(MultiProbe):
    """Testing"""

    def get_behavior(self):
        return TPBehavior


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


class PassiveMatlab(Experiment):
    """ Passive Matlab stimulation
    """
    def __init__(self, logger, timer, params):
        self.stim = eval(params['stim_type'])(logger, self.get_behavior())
        super(PassiveMatlab, self).__init__(logger, timer, params)

    def prepare(self):
        self.stim.setup()
        self.stim.prepare()  # prepare stimulus

    def pre_trial(self):
        self.stim.init_trial()  # initialize stimulus

    def trial(self):
        return self.stim.trial.done()

    def get_behavior(self):
        return DummyProbe

    def run(self):
        return self.logger.get_setup_state() == 'stimRunning' and not self.stim.stimulus_done()

    def cleanup(self):
        self.beh.cleanup()
        self.stim.cleanup()
        self.stim.close()


class PassiveMatlabReward(PassiveMatlab):
    """ Passive Matlab with reward in between scans"""

    def on_hold(self, status=True):
        if not status:  # remove probe
            self.beh.get_off_position()
        else:
            self.beh.get_in_position()
            probe = self.beh.is_licking()
            if probe == 1:
                self.beh.water_reward(1)

    def get_behavior(self):
        return TPBehavior


class ActiveMatlab(Experiment):
    """ Rewarded conditions with Matlab
    """
    def __init__(self, logger, timer, params):
        self.stim = eval(params['stim_type'])(logger, self.get_behavior())
        super(ActiveMatlab, self).__init__(logger, timer, params)

    def prepare(self):
        self.stim.setup()
        self.stim.prepare()  # prepare stimulus

    def pre_trial(self):
        self.stim.init_trial()  # initialize stimulus
        self.reward_probe = self.stim.mat.stimulus.get_reward_probe(self, self.logger.get_trial_key())
        self.beh.is_licking()

    def trial(self):
        probe = self.beh.is_licking()
        if probe > 0:
            if self.reward_probe == probe:
                print('Correct!')
                self.reward(probe)
        return self.stim.trial.done()

    def get_behavior(self):
        return SerialProbe

    def run(self):
        return self.logger.get_setup_state() == 'stimRunning' and not self.stim.stimulus_done()

    def reward(self, probe):
        self.beh.water_reward(probe)

    def cleanup(self):
        self.beh.cleanup()
        self.stim.cleanup()
        self.stim.close()


class CenterPort(Experiment):
    """2AFC with center init position"""

    def __init__(self, logger, timer, params):
        self.post_wait = 0
        super(CenterPort, self).__init__(logger, timer, params)

    def prepare(self):
        self.conditions, self.probes = self.logger.log_conditions(self.stim.get_condition_table())  # log conditions
        self.stim.setup()
        self.stim.prepare(self.conditions)  # prepare stimulus

    def pre_trial(self):
        cond = self._get_new_cond()
        self.reward_probe = (RewardCond() & self.logger.session_key & dict(cond_idx=cond)).fetch1('probe')
        is_ready, ready_time = self.beh.is_ready()
        while self.logger.get_setup_state() == 'running' and (not is_ready or ready_time < self.ready_wait):
            time.sleep(.1)
            is_ready, ready_time = self.beh.is_ready()
        if self.logger.get_setup_state() == 'running':
            print('Starting trial!')
            self.stim.init_trial(cond)
            self.beh.is_licking()

    def trial(self):
        if self.logger.get_setup_state() != 'running':
            return True
        self.stim.present_trial()  # Start Stimulus
        probe = self.beh.is_licking()
        if probe > 0:
            self.probe_bias = np.concatenate((self.probe_bias[1:], [probe]))
            if self.reward_probe == probe:
                print('Correct!')
                self.reward(probe)
                return True
            else:
                print('Wrong!')
                self.punish(probe)
                return True  # break trial
        else:
            return False

    def post_trial(self):
        self.stim.stop_trial()  # stop stimulus when timeout
        self.timer.start()
        while self.timer.elapsed_time()/1000 < self.post_wait and self.logger.get_setup_state() == 'running':
            time.sleep(0.5)
        self.post_wait = 0

    def inter_trial(self):
        if self.beh.is_licking():
            self.timer.start()

    def punish(self, probe):
        self.post_wait = self.timeout

    def reward(self, probe):
        self.beh.water_reward(probe)


class DummyCenterPort(CenterPort):
    """Testing"""

    def get_behavior(self):
        return DummyProbe