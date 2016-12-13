import datajoint as dj
from Stimulus import *
from pygame.locals import *
from pipeline import vis
import io, imageio, pygame, sys, Socket, os
import numpy as np


schema = dj.schema('pipeline_behavior', locals())


def erd():
    """for convenience"""
    dj.ERD(schema).draw()

@schema
class ExperimentType(dj.Lookup):
    definition = """
    # Experiment type
    exp_type : char(10) # experiment schema
    ---
    description = '' : varchar(2048) # some description of the experiment
    """

@schema
class Task(dj.Lookup):
    definition = """
    # Behavioral experiment parameters
    task_idx                     : int             # task identification number
    ---
    -> ExperimentType
    intertrial_duration = 30     : int  # time in between trials (s)
    trial_duration = 30          : int  # trial time (s)
    timeout_duration = 180       : int  # timeout punishment delay (s)
    airpuff_duration = 400       : int  # duration of positive punishment (ms)
    response_interval = 1000     : int  # time before a new lick is considered a valid response (ms)
    reward_amount = 8            : int  # microliters of liquid
    conditions                   : varchar(4095) # stimuli to be presented (array of dictionaries)
    description =''              : varchar(2048) # task description
    """

@schema
class MouseWeight(dj.Manual):
    definition = """
    # Weight of the animal
    animal_id                    : int # animal id
    timestamp=CURRENT_TIMESTAMP  : timestamp
    ---
    weight                       : float # in grams
    """

@schema
class Session(dj.Manual):
    definition = """
    # Behavior session info
    animal_id                    : int # animal id
    session_id                   : smallint        # session number
    ---
    intertrial_duration          : int  # time in between trials (s)
    trial_duration               : int  # trial time (s)
    timeout_duration             : int  # timeout punishment delay (s)
    airpuff_duration             : int  # duration of positive punishment (ms)
    response_interval            : int  # time before a new lick is considered a valid response (ms)
    reward_amount                : int  # microliters of liquid
    setup                        : varchar(256)    # computer id
    session_tmst                 : timestamp       # session timestamp
    notes =''                    : varchar(2048) # session notes
    """

    @property
    def populate(self, key):
        key['setup'] = socket.gethostname()


@schema
class Condition(dj.Manual):
    definition = """
    # unique stimulus conditions
    -> Session
    cond_idx                 : smallint        # unique condition index
    ---
    """

@schema
class Movie(dj.Lookup):
    definition = """
    # movies used for generating clips and stills
    movie_name           : char(8)                      # short movie title
    ---
    path                 : varchar(255)                 #
    movie_class          : enum('mousecam','object3d','madmax') #
    original_file        : varchar(255)                 #
    file_template        : varchar(255)                 # filename template with full path
    file_duration        : float                        # (s) duration of each file (must be equal)
    codec="-c:v libx264 -preset slow -crf 5" : varchar(255)                 #
    movie_description    : varchar(255)                 # full movie title
    """

    class Still(dj.Part):
        definition = """
        # Cached still frames from the movie
        -> Movie
        still_id             : int                          # ids of still images from the movie
        ---
        still_frame          : longblob                     # uint8 grayscale movie
        """

    class Clip(Stimulus, dj.Part):
        definition = """
        # Clips from movies
        -> Movie
        clip_number          : int                          # clip index
        ---
        file_name            : varchar(255)                 # full file name
        clip                 : longblob                     #
        """

        def __init__(self):
            self.curr_frame = 1
            self.vid = []
            self.clock = pygame.time.Clock()
            self.pos = (0, 0)
            self.vsize = (0, 0)

        def prepare(self, key):

            path = '~/stimuli/'  # default path to copy clips
            if not os.path.isdir(path):  # create path if necessary
                os.makedirs(path)

            clips, names = (self & key).fetch['clip_number', 'file_name']
            for iclip in clips:
                if not os.path.isfile(path + names[iclip - 1]):
                    (self & key.update(clip_number=iclip)).fetch1['clip'].tofile(path + names[iclip - 1])

        def init_trial(self, cond):

            clip_info = (vis.Movie.Clip() * vis.Movie() & cond).fetch1()
            self.vid = imageio.get_reader(io.BytesIO(clip_info['clip'].tobytes()), 'ffmpeg')
            self.vsize = (clip_info['frame_width'], clip_info['frame_height'])
            self.pos = np.divide(self.size, 2) - np.divide(self.size, 2)
            self.stopped = False


        def showTrial(self):
            if self.curr_frame < range(self.vid.get_length()):

                py_image = pygame.image.frombuffer(self.vid.get_next_data(), self.vsize, "RGB")
                self.screen.blit(py_image, self.pos)
                pygame.display.update()
                self.curr_frame += 1
                self.clock.tick_busy_loop(30)
            else:
                self.stopTrial()

        def stopTrial(self):
            self.vid.close()
            self.curr_frame = 1
            self.stopped = True
@schema
class MovieClipCond(dj.Manual):
    definition = """
    # movie clip conditions
    -> Condition
    ---
    -> Movie.Clip
    """

@schema
class Trial(dj.Manual):
    definition = """
    # Trial information
    -> Session
    -> Condition
    trial_idx                : smallint        # unique condition index
    ---
    start_time               : int             # start time from session start (ms)
    end_time                 : int             # end time from session start (ms)
    """

@schema
class Lick(dj.Manual):
    definition = """
    # Lick timestamps
    -> Session
    lick_time	     	  	: int           	# time from session start (ms)
    ---
    """

@schema
class LiquidDelivery(dj.Manual):
    definition = """
    # Liquid delivery timestamps
    -> Session
    lick_time			    : int 	            # time from session start (ms)
    ---
    """

@schema
class AirpuffDelivery(dj.Manual):
    definition = """
    # Air puff delivery timestamps
    -> Session
    lick_time		    	: int 	            # time from session start (ms)
    ---
    """