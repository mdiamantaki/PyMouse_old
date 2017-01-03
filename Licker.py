import pygame
from Timer import *


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
