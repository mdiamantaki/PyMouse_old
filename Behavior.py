import datajoint as dj

schema = dj.schema('pipeline_behavior', locals())


def erd():
    """for convenience"""
    dj.ERD(schema).draw()

@schema
class ExperimentTypes(dj.Lookup):
    definition = """
    # Experiment type
    exp_type : char(10) # experiment type short name
    ---
    description = '' : varchar(2048) # some description of the experiment
    """

@schema
class Tasks(dj.Lookup):
    definition = """
    # Behavioral experiment parameters
    task                         : int             # task identification number
    ---
    -> ExperimentType
    intertrial_duration = 30000  : int  # time in between trials (ms)
    trial_duration = 30000       : int  # trial time (ms)
    timeout_duration = 180000    : int  # timeout punishment delay (ms)
    airpuff_duration = 400       : int  # duration of positive punishment (ms)
    response_interval = 1000     : int  # time before a new lick is considered a valid response (ms)
    reward_amount = 8            : int  # microliters of liquid
    stimuli                      : varchar(4095) # stimuli to be presented (array of dictionaries)
    rewarded_stimuli             : varchar(4095) # stimuli to be rewarded (array of dictionaries)
    description =''              : varchar(2048) # task description
    """

@schema
class MouseWeights(dj.Manual):
    definition = """
    # Weight of the animal
    -> mice.Mice
    timestamp=CURRENT_TIMESTAMP  : timestamp
    ---
    weight                       : float # in grams
    """


@schema
class Sessions(dj.Manual):
    definition = """
    # Behavior session info
    -> mice.Mice
    session_id                   : smallint        # session number
    ---
    -> Tasks
    setup                        : varchar(256)    # computer id
    session_tmst                 : timestamp       # session timestamp
    """

    class Conditions(dj.Manual):
        definition = """
        # unique stimulus conditions
        -> Sessions
        cond_idx                 : smallint        # unique condition index
        ---
        """

    class Trials(dj.Manual):
        definition = """
        # Trial information
        -> Sessions
        -> Conditions
        trial_idx                : int             # unique condition index
        ---
        start_time               : double          # start time from session start (ms)
        end_time                 : double          # end time from session start (ms)
        """


    class Licks(dj.Manual):
        definition = """
        # Lick timestamps
        -> Sessions
        lick_time			: double 	# time from session start (ms)
        ---
        """

    class LiquidDelivery(dj.Manual):
        definition = """
        # Liquid delivery timestamps
        -> Sessions
        lick_time			: double 	# time from session start (ms)
        ---
        """

    class AirpuffDelivery(dj.Manual):
        definition = """
        # Air puff delivery timestamps
        -> Sessions
        lick_time			: double 	# time from session start (ms)
        ---
        """