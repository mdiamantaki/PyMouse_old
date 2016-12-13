import pygame
import numpy as np

class Stimulus:
    """ This class handles the stimulus presentation
    """

    def __init__(self, w=100, h=100, loc=[0, 0]):
        pygame.init()
        self.size = (w, h)
        self.vcolor = [88, 88, 88]
        self.loc = loc
        self.screen = pygame.display.set_mode(self.size, pygame.NOFRAME)
        self.stopped = True
        self.unshow()

    def init_block(self):  # create random block of all conditions

        image_idx = self.index[0]
        if np.size(self.index) > 1:
            self.index = self.index[1:]
        else:
            self.init_block()
        self.index = np.random.permutation(self.block_sz)

    def prepare(self, key):  # prepares stuff for presentation before experiment starts
        pass

    def init_trial(self): # initialize stuff for each trial
        pass

    def showTrial(self):  # start trial
        pass

    def stopTrial(self):  # stop trial
        pass

    def unshow(self):  # refresh background

        self.screen.fill(self.vcolor)
        pygame.display.flip()

    def color(self, color):  # updated background color
        self.vcolor = color

    def close(self):  # exit
        pygame.quit()
