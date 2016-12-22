import pygame
from pygame.locals import *


class Stimulus:
    """ This class handles the stimulus presentation
    use function overrides for each stimulus class
    """

    def __init__(self, cond_table):
        pygame.init()
        self.cond_table = cond_table()
        self.size = (256, 144)
        self.vcolor = [88, 88, 88]
        self.loc = (0, 0)
        self.screen = pygame.display.set_mode(self.size, pygame.NOFRAME)
        self.stopped = True
        self.unshow()

    def init_block(self):  # create random block of all conditions
        pass

    def prepare(self, key):  # prepares stuff for presentation before experiment starts
        self.cond_table.prepare(key)

    def init_trial(self, key):  # initialize stuff for each trial
        self.cond_table.init_trial(key, self.size)

    def show_trial(self):  # start trial
        self.cond_table.show_trial(self.screen)
        self.update_event()

    def stop_trial(self):  # stop trial
        self.cond_table.stop_trial()
        self.update_event()

    def pause(self):  # pause stimulus presentation
        pass

    def update_event(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()

    def unshow(self):  # refresh background
        self.screen.fill(self.vcolor)
        pygame.display.flip()
        self.update_event()

    def color(self, color):  # updated background color
        self.vcolor = color

    @staticmethod
    def close():  # exit
        pygame.display.quit()
        pygame.quit()
