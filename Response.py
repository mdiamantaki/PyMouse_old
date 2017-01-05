from Behavior import *
import pygame, time


class Response:
    """ this class handles the response to the licks
    """
    def __init__(self, logger, timer, params):
        self.beh = Behavior(logger, params)
        self.logger = logger
        self.air_dur = params['airpuff_duration']
        self.timeout = params['timeout_duration']
        self.silence = params['silence_thr']
        self.timer = timer
        self.reward_probe = []

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


class MultiProbeResponse(Response):
    """2AFC & GoNOGo tasks"""
    def pre_trial(self, cond):
        self.reward_probe = (RewardCond() & self.logger.session_key & dict(cond_idx=cond)).fetch1['probe']
        probe = self.beh.is_licking()

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

    def inter_trial(self):
        if self.beh.is_licking():
            self.timer.start()
            self.timer.add_delay(self.timeout)
        elif self.beh.inactivity_time() > self.silence:
            while not self.beh.is_licking():
                time.sleep(1)

    def punish(self, probe):
        self.beh.punish_with_air(probe, self.air_dur)

    def reward(self, probe):
        self.beh.water_reward(probe)


class dummyResponse(Response):
    """Testing"""
    def __init__(self, logger, timer, params):
        self.air_dur = params['airpuff_duration']
        self.timeout = params['timeout_duration']
        self.silence = params['silence_thr']
        self.logger = logger
        self.timer = timer
        self.reward_probe = []

    def trial(self):
        probe = self.__lick()
        if probe > 0:
            if self.reward_probe == probe:
                self.reward(probe)
            else:
                self.punish(probe)
            return True  # break trial
        else:
            return False

    def inter_trial(self):
        if self.__lick():
            print('wait!')
            self.timer.start()
            self.timer.add_delay(self.timeout)

    def punish(self, probe):
        print('Punishing!')
        self.logger.log_air()

    def reward(self, probe):
        print('Rewarding!')
        self.logger.log_reward()

    def __lick(self):
        """Simulate licks with keyboard"""
        probe = 0
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.logger.log_lick(1)
                    probe = 1
                if event.key == pygame.K_RIGHT:
                    self.logger.log_lick(2)
                    probe = 2
        return probe


class FreeWater(Response):
    """Reward upon lick"""
    def trial(self):
        probe = self.beh.is_licking()
        if probe:
            self.beh.water_reward(probe)



