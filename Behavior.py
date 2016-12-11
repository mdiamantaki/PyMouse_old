import datajoint as dj
import socket

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

    class Clip(dj.Part):
        definition = """
        # Clips from movies
        -> Movie
        clip_number          : int                          # clip index
        ---
        file_name            : varchar(255)                 # full file name
        clip                 : longblob                     #
        """

        @staticmethod
        def prepare(self, key):
            key['setup'] = socket.gethostname()

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