from pygame.locals import *
import io, imageio, pygame, os
import numpy as np
from Behavior import *


class Stimulus:
    """ This class handles the stimulus presentation
    use function overrides for each stimulus class
    """

    def __init__(self):
        pygame.init()
        self.path = 'stimuli/'  # default path to copy local stimuli
        self.size = (256, 144)
        self.vcolor = [88, 88, 88]
        self.loc = (0, 0)
        self.screen = pygame.display.set_mode(self.size, pygame.NOFRAME)
        self.stopped = True
        self.conditions = []
        self.indexes = []
        self.unshow()

    def get_curr_cond(self):  # get curr condition & create random block of all conditions
        cond = self.conditions[self.indexes[0]]
        if np.size(self.conditions) > 1:
            self.indexes = self.indexes[1:]
        else:
            self.indexes = np.random.permutation(np.size(self.conditions))
        return cond

    def prepare(self, conditions):  # prepares stuff for presentation before experiment starts
        pass

    def init_trial(self, key):  # initialize stuff for each trial
        pass

    def show_trial(self):  # start trial
        pass

    def stop_trial(self):  # stop trial
        pass

    def get_condition_table(self):
        pass

    def unshow(self):  # updated background color
        self.screen.fill(self.vcolor)
        self.flip()

    @staticmethod
    def flip():
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()

    @staticmethod
    def close():  # exit
        pygame.display.quit()
        pygame.quit()


class Movies(Stimulus):

    def prepare(self, conditions):
        self.conditions = conditions

        if not os.path.isdir(self.path):  # create path if necessary
            os.makedirs(self.path)

        for key in (Movie.Clip() * MovieClipCond() & conditions).fetch.as_dict:
            filename = self.path + key['file_name']
            if not os.path.isfile(filename):
                (Movie.Clip() & key).fetch1['clip'].tofile(filename)

    def init_trial(self):
        cond = self.get_curr_cond()
        self.curr_frame = 1
        self.clock = pygame.time.Clock()

        clip_info = (Movie() * Movie.Clip() * MovieClipCond() & dict(cond_idx=cond)).fetch1()
        self.vid = imageio.get_reader(io.BytesIO(clip_info['clip'].tobytes()), 'ffmpeg')
        self.vsize = (clip_info['frame_width'], clip_info['frame_height'])
        self.pos = np.divide(self.size, 2) - np.divide(self.size, 2)

    def show_trial(self):
        if self.curr_frame < (self.vid.get_length()):
            py_image = pygame.image.frombuffer(self.vid.get_next_data(), self.vsize, "RGB")
            self.screen.blit(py_image, self.pos)
            self.flip()
            self.curr_frame += 1
            self.stopped = False
            self.clock.tick_busy_loop(30)
        else:
            self.stop_trial()

    def stop_trial(self):
        self.vid.close()
        self.unshow()
        self.stopped = True

    def get_condition_table(self):
        return MovieClipCond
