from Behavior import *


class Response:
    """ this class handles the licks
    """
    def __init__(self, logger, timer, params):
        self.logger = logger
        self.params = params
        self.timer = timer

    def punish(self):
        self.give_air()
        self.logger.log_air()

    def reward(self):
        self.give_liquid()
        self.logger.log_reward()

    def give_air(self):
        pass

    def give_liquid(self):
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
            print('correct!')
        else:
            print('wrong!')

        return True  # break trial

    def trial_no_lick(self):
        if self.reward_probe == 0:
            print('correct!')
        else:
            print('wrong!')

    def inter_trial_lick(self, probe):
        print('wait!')
        self.timer.start()


class PassiveResponse(Response):
    def trial_lick(self, probe):
        self.reward()
