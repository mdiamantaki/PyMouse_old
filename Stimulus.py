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

        self.unshow()

    def prepare(self, key):  # to be overridden
        pass

    def init_block(self):

        self.index = np.random.permutation(self.block_sz)

    def init_trial(self):

        image_idx = self.index[0]
        if np.size(self.index) > 1:
            self.index = self.index[1:]
        else:
            self.init_block()

        self.myVideoPlayer = VideoPlayer([480, 320], fullscreen=False, soundrenderer="pyaudio", loop=False)
        self.myVideoPlayer.load_media(self.videos[image_idx])
        self.myVideoPlayer.play()

        return image_idx

    def showTrial(self):
        # flip
        self.myVideoPlayer.play_frame()

    def stopTrial(self):
        self.myVideoPlayer.quit()

    def unshow(self):

        self.screen.fill(self.vcolor)
        pygame.display.flip()

    def color(self, color):
        self.vcolor = color

    def close(self):
        pygame.quit()
