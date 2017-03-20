from LickSpout import *
from Timer import *
import pygame


class Behavior:
    """ This class handles the behavior variables """
    def __init__(self, logger, params):
        self.resp_int = params['response_interval']
        self.resp_timer = Timer()
        self.resp_timer.start()
        self.logger = logger

    def is_licking(self):
        return False

    def is_running(self):
        return False

    def water_reward(self, probe):
        print('Giving Water!')

    def punish_with_air(self, probe, air_dur=200):
        print('Punishing with Air!')

    def inactivity_time(self):  # in minutes
        return 0

    def cleanup(self):
        pass


class RPBehavior(Behavior):
    """ This class handles the behavior variables for RP """
    def __init__(self, logger, params):
        self.licker = Licker(logger)
        self.valves = ValveControl(logger)
        super(RPBehavior, self).__init__(logger, params)

    def is_licking(self):
        probe = self.licker.lick()
        if self.resp_timer.elapsed_time() < self.resp_int:
            probe = 0
        return probe

    def water_reward(self, probe):
        self.valves.give_liquid(probe)

    def punish_with_air(self, probe, air_dur=200):
        self.valves.give_air(probe, air_dur)

    def inactivity_time(self):  # in minutes
        return numpy.minimum(self.licker.timer_probe1.elapsed_time(),
                             self.licker.timer_probe2.elapsed_time()) / 1000 / 60

    def cleanup(self):
        self.licker.cleanup()


class DummyProbe(Behavior):
    def __init__(self, logger, params):
        self.lick_timer = Timer()
        self.lick_timer.start()
        super(DummyProbe, self).__init__(logger, params)

    def is_licking(self):
        probe = 0
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.logger.log_lick(1)
                    probe = 1
                    self.lick_timer.start()
                if event.key == pygame.K_RIGHT:
                    self.logger.log_lick(2)
                    probe = 2
        return probe

    def inactivity_time(self):  # in minutes
        return self.lick_timer.elapsed_time() / 1000 / 60



