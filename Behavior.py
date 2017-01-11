from LickSpout import *
from Timer import *


class Behavior:
    """ This class handles the behavior variables """
    def __init__(self, logger, params):
        self.resp_int = params['response_interval']
        self.licker = Licker(logger)
        self.valves = ValveControl(logger)
        self.lick_timer = Timer()
        self.lick_timer.start()

    def is_licking(self):
        probe = self.licker.lick()

        if self.lick_timer.elapsed_time() < self.resp_int:
            probe = 0

        return probe

    def is_running(self):
        return False

    def water_reward(self, probe):
        self.valves.give_liquid(probe)

    def punish_with_air(self, probe, air_dur=400):
        self.valves.give_air(probe, air_dur)

    def inactivity_time(self):  # in minutes
        return numpy.minimum(self.licker.timer_probe1.elapsed_time(),
                             self.licker.timer_probe2.elapsed_time())/1000/60

