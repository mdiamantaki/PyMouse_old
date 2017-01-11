from pygame.locals import *
import io, imageio, pygame, os
from Experiment import *
import numpy as np


class Stimulus:
    """ This class handles the stimulus presentation
    use function overrides for each stimulus class
    """

    def __init__(self, logger):
        # setup parameters
        self.path = 'stimuli/'     # default path to copy local stimuli
        self.size = (800, 480)     # window size
        self.color = [88, 88, 88]  # default background color
        self.loc = (0, 0)          # default starting location of stimulus surface
        self.fps = 30              # default presentation framerate

        # initilize parameters
        self.logger = logger
        self.isrunning = False
        self.flip_count = 0
        self.conditions = []
        self.indexes = []

    def setup(self):
        """ Pygame setup"""
        pygame.init()
        self.screen = pygame.display.set_mode(self.size, NOFRAME | HWSURFACE | DOUBLEBUF | RESIZABLE)
        self.unshow()
        pygame.mouse.set_visible(0)
        pygame.display.toggle_fullscreen()

    def prepare(self):
        """prepares stuff for presentation before experiment starts"""
        # log conditions
        self.conditions = self.logger.log_conditions(self.get_condition_table())

    def init_trial(self):
        """initialize stuff for each trial"""
        pass

    def show_trial(self):
        """trial presentation method"""
        pass

    def stop_trial(self):
        """stop trial"""
        pass

    def get_condition_table(self):
        """method to get the stimulus condition table"""
        pass

    def get_experiment(self):
        """method to get the type of experiment"""
        return Experiment

    def unshow(self):
        """update background color"""
        self.screen.fill(self.color)
        self.flip()

    def _get_new_cond(self):
        """Get curr condition & create random block of all conditions
        Should be called within init_trial
        """
        if np.size(self.indexes) == 0:
            self.indexes = np.random.permutation(np.size(self.conditions))
        cond = self.conditions[self.indexes[0]]
        self.indexes = self.indexes[1:]
        return cond

    def encode_photodiode(self):
        """Encodes the flip number n in the flip amplitude.
        Every 32 sequential flips encode 32 21-bit flip numbers.
        Thus each n is a 21-bit flip number:
        FFFFFFFFFFFFFFFFCCCCP
        P = parity, only P=1 encode bits
        C = the position within F
        F = the current block of 32 flips
        """
        n = self.flip_count + 1
        amp = 127 * (n & 1) * (2 - (n & (1 << (((np.int64(np.floor(n / 2)) & 15) + 6) - 1)) != 0))
        surf = pygame.Surface((50, 50))
        surf.fill((amp, amp, amp))
        self.screen.blit(surf, (0, 0))

    def flip(self):
        """ Main flip method"""
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()

        self.flip_count += 1

    @staticmethod
    def close():
        """Close stuff"""
        pygame.mouse.set_visible(1)
        pygame.display.quit()
        pygame.quit()


class Movies(Stimulus):
    """ This class handles the presentation of Movies"""
    def init_trial(self):
        cond = self._get_new_cond()
        self.curr_frame = 1
        self.clock = pygame.time.Clock()
        clip_info = (Movie() * Movie.Clip() * MovieClipCond() & dict(cond_idx=cond) & self.logger.session_key).fetch1()
        self.vid = imageio.get_reader(io.BytesIO(clip_info['clip'].tobytes()), 'ffmpeg')
        self.vsize = (clip_info['frame_width'], clip_info['frame_height'])
        self.pos = np.divide(self.size, 2) - np.divide(self.vsize, 2)
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
            self.clock.tick_busy_loop(self.fps)
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

    def get_experiment(self):
        return Dummy


class RPMovies(Stimulus):
    """ This class handles the presentation of Movies with an optimized library for Raspberry pi"""
    def prepare(self):
        from omxplayer import OMXPlayer

        self.player = OMXPlayer
        # log conditions
        self.conditions = self.logger.log_conditions(self.get_condition_table())

        # store local copy of files
        if not os.path.isdir(self.path):  # create path if necessary
            os.makedirs(self.path)
        for cond_idx in self.conditions:
            filename = self.path + \
                       (Movie.Clip() * MovieClipCond() & dict(cond_idx=cond_idx) & self.logger.session_key).fetch1[
                           'file_name']
            if not os.path.isfile(filename):
                (Movie.Clip() * MovieClipCond() & dict(cond_idx=cond_idx) & self.logger.session_key).fetch1[
                    'clip'].tofile(filename)

    def init_trial(self):
        cond = self._get_new_cond()
        self.isrunning = True

        filename = self.path + (Movie.Clip() * MovieClipCond() & dict(cond_idx=cond) &
                                     self.logger.session_key).fetch1['file_name']

        # log start trial
        self.logger.start_trial(cond)

        # start video
        self.vid = self.player(filename)

        return cond

    def stop_trial(self):
        self.vid.quit()
        self.unshow()
        self.isrunning = False

        # log trial
        self.logger.log_trial(self.flip_count)

    def get_condition_table(self):
        return MovieClipCond

    def get_experiment(self):
        return MultiProbe


class Gratings(Stimulus):
    """ This class handles the presentation orientations"""
    def prepare(self):
        self.conditions = self.logger.log_conditions(self.get_condition_table())
        self.clock = pygame.time.Clock()
        self.stim_conditions = dict()
        for cond in self.conditions:
            params = (GratingCond() & dict(cond_idx=cond) & self.logger.session_key).fetch1()
            params['grating'] = self.__make_grating(params['spatial_period'],
                                                    params['direction'],
                                                    params['phase'])
            self.stim_conditions[cond] = params


    def init_trial(self):
        cond = self._get_new_cond()

        # get condition parameters
        self.grating = self.stim_conditions[cond]['grating']
        self.lamda = self.stim_conditions[cond]['spatial_period']
        self.frame_step = self.lamda * (self.stim_conditions[cond]['temporal_freq'] / self.fps)
        self.frame_idx = 0
        self.xt = np.cos((self.stim_conditions[cond]['direction'] / 180) * np.pi)
        self.yt = np.sin((self.stim_conditions[cond]['direction'] / 180) * np.pi)

        # log start trial
        self.logger.start_trial(cond)
        self.isrunning = True
        return cond

    def show_trial(self):
        displacement = np.mod(self.frame_idx * self.frame_step, self.lamda)
        self.screen.blit(self.grating,
                         (-self.lamda + self.yt * displacement,
                          -self.lamda + self.xt * displacement))
        self.encode_photodiode()
        self.flip()
        self.frame_idx += 1
        self.clock.tick_busy_loop(self.fps)

    def stop_trial(self):
        self.unshow()
        self.isrunning = False
        self.logger.log_trial(self.flip_count)  # log trial

    def get_condition_table(self):
        return GratingCond

    def __make_grating(self, lamda=50, theta=0, phase=0):
        """ Makes an oriented grating
        lamda: wavelength (number of pixels per cycle)
        theta: grating orientation in degrees
        phase: phase of the grating
        """
        w = np.max(self.size) + 2 * lamda

        freq = w/lamda  # compute frequency from wavelength
        # make linear ramp
        x0 = np.linspace(0, 1, w) - .5
        xm, ym = np.meshgrid(x0, x0)

        # Change orientation by adding Xm and Ym together in different proportions
        theta_rad = (theta/180) * np.pi
        xt = xm * np.cos(theta_rad)
        yt = ym * np.sin(theta_rad)

        im = np.floor((np.sin(((xt + yt) * freq * 2 * np.pi) + phase)+1)*127)
        grating = np.transpose(np.tile(im, [3, 1, 1]), (1, 2, 0))
        return pygame.surfarray.make_surface(grating)

    def get_experiment(self):
        return Dummy


class PassiveMovies(RPMovies):
    """ This class handles the presentation of Movies as a pasive task"""
    def get_experiment(self):
        return FreeWater


class NoStimulus(Stimulus):
    """ This class does not present any stimulus and water is delivered upon a lick"""

    def setup(self):
        """ Pygame setup"""
        pygame.init()
        self.screen = pygame.display.set_mode((100, 100))
        self.unshow()

    def init_trial(self):
        self.isrunning = True

    def get_experiment(self):
        #return FreeWater
        return TestExp
