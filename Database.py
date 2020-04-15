import datajoint as dj
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.dates import DateFormatter
import numpy as np

schema = dj.schema('pipeline_behavior')
schema2 = dj.schema('pipeline_stimulus')

def erd():
    """for convenience"""
    dj.ERD(schema).draw()


@schema
class SetupInfo(dj.Lookup):
    definition = """
    #
    setup                  : varchar(256)   # Setup name
    ---
    ip                     : varchar(16)    # setup IP address
    state="ready"          : enum('ready','running','stopped','sleeping')  #
    animal_id=null         : int # animal id
    task_idx=null          : int             # task identification number
    task="train"           : enum('train','calibrate')
    last_ping=null         : timestamp
    """

@schema
class LiquidCalibration(dj.Manual):
    definition = """
    # Liquid delivery calibration sessions for each probe
    setup                        : varchar(256)   # Setup name
    probe                        : int            # probe number
    date                         : date           # session date (only one per day is allowed)
    """

    class PulseWeight(dj.Part):
        definition = """
        # Data for volume per pulse duty cycle estimation
        -> LiquidCalibration
        pulse_dur                : int   # duration of pulse in ms
        ---
        pulse_num                : int   # number of pulses
        weight                   : float # weight of total liquid released in gr
        """


@schema
class ExperimentType(dj.Lookup):
    definition = """
    # Experiment type
    exp_type : char(128) # experiment schema
    ---
    description = '' : varchar(2048) # some description of the experiment
    """

    contents = [
        ('MultiProbe', '2AFC & GoNOGo tasks with lickspout'),
        ('DummyMultiProbe', 'Same as Multiprobe but with a dummy probe'),
        ('FreeWater', 'Reward upon lick'),
        ('ProbeTest', 'Testing probes'),
        ('Pasive', 'No reward/punishment'),
    ]


@schema
class StimulusType(dj.Lookup):
    definition = """
    # Stimulus type
    stim_type : char(128) # stimulus schema
    ---
    description = '' : varchar(2048) # some description of the experiment
    """

    contents = [
        ('Movies', 'Typical movies stimulus'),
        ('RPMovies', 'Same as Movies but for Raspberry pi'),
        ('Gratings', 'Orientation Gratings'),
        ('NoStimulus', 'Free water condition with no stimulus'),
    ]


@schema
class Task(dj.Lookup):
    definition = """
    # Behavioral experiment parameters
    task_idx                     : int             # task identification number
    ---
    -> ExperimentType
    -> StimulusType
    intertrial_duration = 30     : int  # time in between trials (s)
    trial_duration = 30          : int  # trial time (s)
    timeout_duration = 180       : int  # timeout punishment delay (s)
    airpuff_duration = 400       : int  # duration of positive punishment (ms)
    response_interval = 1000     : int  # time before a new lick is considered a valid response (ms)
    reward_amount = 8            : int  # microliters of liquid
    silence_thr = 30             : int  # lickless period after which stimulus is paused (min)
    conditions                   : varchar(4095) # stimuli to be presented (array of dictionaries)
    description =''              : varchar(2048) # task description
    start_time=null              : time
    stop_time=null               : time
    """

    contents = [
        (1,'MultiProbe','RPMovies', 30, 30, 180, 400, 1000, 8, 30,
         "[{'probe':[1], 'clip_number':list(range(1,3)), 'movie_name':['obj1v4']},\
         {'probe':[2], 'clip_number':list(range(1,3)), 'movie_name':['obj2v4']}]",
         '3d object experiment'),
    ]


@schema
class CalibrationTask(dj.Lookup):
    definition = """
    # Calibration parameters
    task_idx                     : int             # task identification number
    ---
    probe='[1,2]'                : varchar(128)    # probe number
    pulse_dur                    : int             # duration of pulse in ms
    pulse_num                    : int             # number of pulses
    pulse_interval               : int             # interval between pulses in ms
    save='yes'                   : enum('yes','no')# store calibration
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
    
    def plot(self, key = 'all'):
        if key == 'all':
            mw = pd.DataFrame((self).fetch())
        else: 
            mw = pd.DataFrame((self & key).fetch())
        
        mice = mw['animal_id'].unique()
        m_count = mw['animal_id'].value_counts()
        k = 0
        for idx in mice:
            w0 = mw[mw['animal_id'] == idx].at[k, 'weight']
            ax = mw[mw['animal_id'] == idx].plot(x='timestamp', y='weight') 
            ax.axhline(0.7*w0, linestyle='--', color='red', label="30%")
            ax.axhline(0.8*w0, linestyle='--', color='pink', label='20%')
            ax.axhline(0.9*w0, linestyle='--', color='green', label='10%')
            plt.xticks(rotation=45)
            plt.ylabel('Mouse Weight (gr)')
            plt.xlabel('Time')
            date_form = DateFormatter("%d-%m-%y")
            ax.xaxis.set_major_formatter(date_form)
            ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
            ax.set_title('Animal_id: %1d' % idx)
            k = k+m_count[idx]
        return ax

    

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


@schema
class Condition(dj.Manual):
    definition = """
    # unique stimulus conditions
    -> Session
    cond_idx                 : smallint        # unique condition index
    ---
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
    last_flip_count          : int             # the last flip number in this trial
    """


@schema
class Lick(dj.Manual):
    definition = """
    # Lick timestamps
    -> Session
    time	     	  	: int           	# time from session start (ms)
    probe               : int               # probe number
    """


@schema
class LiquidDelivery(dj.Manual):
    definition = """
    # Liquid delivery timestamps
    -> Session
    time			    : int 	            # time from session start (ms)
    probe               : int               # probe number
    """
    def plot(self, key = 'all'):
        if key == 'all':
            df = pd.DataFrame((self * Session).fetch())
        else: 
            df = pd.DataFrame((self * Session & key).fetch())
            
        df['new_tmst'] = (df['session_tmst'] - pd.Timestamp("1970-01-01")) // pd.Timedelta('1ms') 
        df['new_tmst'] = df['new_tmst'] + df['time']
        df['new_tmst'] = pd.to_datetime(df['new_tmst'], unit='ms', origin='unix')
        df['new_tmst']= df['new_tmst'].dt.date
        mice = df['animal_id'].unique()
        m_count = df['animal_id'].value_counts()
        t_count = df.groupby(['animal_id'])['new_tmst'].value_counts().sort_index()
        df['total_reward'] = np.nan
        kk=0
        for idx in mice:
            for j in range(len(t_count[idx])):
                df['total_reward'][kk] = t_count[idx][j] * df['reward_amount'][kk]
                kk = kk+t_count[idx][j]
        df['total_reward']= df['total_reward']/1000
        k=0
        for idx in mice:
            ax = df[df['animal_id']==idx].dropna().plot(x='new_tmst', y='total_reward') 
            plt.axhline(y=1, color='r', linestyle='-.')
            plt.xticks(rotation=45)
            plt.ylabel('DeliveredLiquid(ml)')
            date_form = DateFormatter("%d-%m-%y")
            ax.xaxis.set_major_formatter(date_form)
            ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
            ax.set_title('Animal_id: %1d' % idx)
            k = k+m_count[idx]
        return ax

@schema
class AirpuffDelivery(dj.Manual):
    definition = """
    # Air puff delivery timestamps
    -> Session
    time		    	: int 	            # time from session start (ms)
    probe=0             : int               # probe number
    """

@schema
class OdorDelivery(dj.Manual):
    definition = """
    # Odor delivery timestamps
    -> Session
    time		    	: int 	            # time from session start (ms)
    odor_idx=0             : int            # odor number
    """

@schema2
class Movie(dj.Lookup):
    definition = """
    # movies used for generating clips and stills
    movie_name           : char(8)                      # short movie title
    ---
    path                 : varchar(255)                 #
    movie_class          : enum('mousecam','object3d','madmax','multiobject') #
    original_file        : varchar(255)                 #
    file_template        : varchar(255)                 # filename template with full path
    file_duration        : float                        # (s) duration of each file (must be equal)
    codec="-c:v libx264 -preset slow -crf 5" : varchar(255)                 #
    movie_description    : varchar(255)                 # full movie title
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

@schema
class MovieClipCond(dj.Manual):
    definition = """
    # movie clip conditions
    -> Condition
    ---
    -> Movie.Clip
    """

@schema
class GratingCond(dj.Manual):
    definition = """
    # Orientation gratings conditions
    -> Condition
    ---
    direction                : int                    # in degrees (0-360)
    spatial_period           : int                    # pixels/cycle
    temporal_freq            : float                  # cycles/sec
    contrast=100             : int                    # 0-100 Michelson contrast
    phase=0                  : float                  # initial phase in rad
    square=0                 : tinyint                # square wave flag (binary)
    """

@schema
class RewardCond(dj.Manual):
    definition = """
    # reward probe conditions
    -> Condition
    ---
    probe=0        :int         # probe number
    """

@schema
class OdorCond(dj.Manual):
    definition = """
    # reward probe conditions
    -> Condition
    ---
    odor_dur=1000     :int          # odor duration (ms)
    odor_idx=0        :int          # odor index for channel mapping
    odor_name=""      :varchar(255) # name of the odor
    """
