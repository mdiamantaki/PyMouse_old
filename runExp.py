from Logger import *
from Experiment import *
import sys

logger = PCLogger()                                                     # setup logger & timer
logger.log_setup()                                                    # publish IP and make setup available


def do_initialize(lgr):
    """Initialize the stimulation software"""
    lgr.update_setup_state('systemReady')


def do_start_session(lgr):
    """start stimulation session"""
    lgr.init_params()  # clear settings from previous session
    lgr.log_session()  # start session
    lgr.update_setup_state('sessionRunning')


def do_start_stim(lgr):
    """start stimulation trials"""
    p = (Task() & dict(task_idx=lgr.task_idx)).fetch1()  # get parameters
    t = Timer()  # main timer for trials
    e = eval(p['exp_type'])(lgr, t, p)  # get experiment & init
    e.prepare()  # prepare stuff
    lgr.update_setup_state('stimRunning')
    return p, e, t


def do_stop_stim(lgr,exp):
    # # # # # Cleanup # # # # #
    exp.cleanup()
    lgr.update_setup_state('ready')
    lgr.update_setup_state('sessionRunning')


def do_stop_session(lgr,exp):
    do_stop_stim(lgr,exp)
    lgr.update_setup_state('systemReady')


def process_command(lgr,exp,command):
    p = dict
    e = []
    t = []
    #   process command
    if command == 'Initialize':
        # wait for initialization
        do_initialize(lgr)
    elif command == 'startSession':
        do_start_session(lgr)
    elif command == 'startStim':
        p, e, t = do_start_stim(lgr)
    elif command == 'stopStim':
        do_stop_stim(lgr,exp)
    elif command == 'stopSession':
        do_stop_session(lgr,exp)
    else:
        pass
    return p, e, t


# # # # Waiting for instructions loop # # # # #
exprmt = []
while True:

    cmd = logger.get_setup_state_control()
    params, exprmt, timer = process_command(logger, exprmt, cmd)

#   run a trial
    if logger.get_setup_state == 'stimRunning' and not exprmt == [] and exprmt.run():

        # # # # # Pre-Trial period # # # # #
        logger.ping()
        exprmt.pre_trial()

        # # # # # Trial period # # # # #
        timer.start()  # Start countdown for response]
        while timer.elapsed_time() < params['trial_duration'] * 1000:  # response period
            break_trial = exprmt.trial()  # get appropriate response
            if break_trial:
                break  # break if experiment calls for it

        # # # # # Post-Trial Period # # # # #
        exprmt.post_trial()

        # # # # # Intertrial period # # # # #
        timer.start()
        while timer.elapsed_time() < params['intertrial_duration'] * 1000:
            exprmt.inter_trial()
    else:
        time.sleep(0.1)




