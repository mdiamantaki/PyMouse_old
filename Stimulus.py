from pygame.locals import *
import io, imageio, pygame, os
import numpy as np
from Response import *


class Stimulus:
    """ This class handles the stimulus presentation
    use function overrides for each stimulus class
    """

    def __init__(self, logger):
        pygame.init()
        self.path = 'stimuli/'  # default path to copy local stimuli
        self.size = (256, 144)
        self.color = [88, 88, 88]
        self.loc = (0, 0)
        self.screen = pygame.display.set_mode(self.size, pygame.NOFRAME)
        self.isrunning = False
        self.conditions = []
        self.indexes = []
        self.unshow()
        self.logger = logger
        pygame.mouse.set_visible(0)

    def prepare(self):  # prepares stuff for presentation before experiment starts
        pass

    def init_trial(self):  # initialize stuff for each trial
        pass

    def show_trial(self):  # start trial
        pass

    def stop_trial(self):  # stop trial
        pass

    def get_condition_table(self):
        pass

    def get_responder(self):
        return Response

    def unshow(self):  # updated background color
        self.screen.fill(self.color)
        self.flip()

    def _get_new_cond(self):  # get curr condition & create random block of all conditions,
        #  should be called within init_trial
        if np.size(self.indexes) == 0:
            self.indexes = np.random.permutation(np.size(self.conditions))

        cond = self.conditions[self.indexes[0]]
        self.indexes = self.indexes[1:]

        return cond

    @staticmethod
    def flip():
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()

    @staticmethod
    def close():  # exit
        pygame.mouse.set_visible(1)
        pygame.display.quit()
        pygame.quit()


class Movies(Stimulus):

    def prepare(self):

        # log conditions
        self.conditions = self.logger.log_conditions(self.get_condition_table())

        if not os.path.isdir(self.path):  # create path if necessary
            os.makedirs(self.path)

        for cond_idx in self.conditions:
            filename = self.path + (Movie.Clip() * MovieClipCond() & dict(cond_idx=cond_idx) & self.logger.session_key).fetch1['file_name']
            if not os.path.isfile(filename):
                (Movie.Clip() * MovieClipCond() & dict(cond_idx=cond_idx)).fetch1['clip'].tofile(filename)

    def init_trial(self):

        cond = self._get_new_cond()
        self.curr_frame = 1
        self.clock = pygame.time.Clock()
        clip_info = (Movie() * Movie.Clip() * MovieClipCond() & dict(cond_idx=cond) & self.logger.session_key).fetch1()
        self.vid = imageio.get_reader(io.BytesIO(clip_info['clip'].tobytes()), 'ffmpeg')
        self.vsize = (clip_info['frame_width'], clip_info['frame_height'])
        self.pos = np.divide(self.size, 2) - np.divide(self.size, 2)
        self.isrunning = True

        # log start trial
        self.logger.start_trial(cond)

        return cond

    def show_trial(self):
        if self.curr_frame < (self.vid.get_length()):
            py_image = pygame.image.frombuffer(self.vid.get_next_data(), self.vsize, "RGB")
            self.screen.blit(py_image, self.pos)
            self.flip()
            self.curr_frame += 1
            self.clock.tick_busy_loop(30)
        else:
            self.isrunning = False

    def stop_trial(self):
        self.vid.close()
        self.unshow()
        self.isrunning = False

        # log trial
        self.logger.log_trial()

    def get_condition_table(self):
        return MovieClipCond

    def get_responder(self):
        return MultiProbeResponse


class PassiveMovies(Movies):
    def get_responder(self):
        return FreeWater


class NoStimulus(Stimulus):

    def init_trial(self):
        self.isrunning = True

    def get_responder(self):
        return FreeWater
