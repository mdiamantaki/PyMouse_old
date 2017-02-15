from Logger import *
from Stimulus import *
import sys

# setup loger & timer
logger = Logger()
logger.log_setup()  # publish IP and make setup available
timer = Timer()  # main timer for trials

while not logger.get_setup_state() == 'stopped':

    # wait for remote start
    while logger.get_setup_state() == 'ready':
        time.sleep(1)

    # start session
    logger.log_session()

    # get parameters
    params = (Task() & dict(task_idx=logger.task_idx)).fetch1()

    # prepare stimulus
    stim = eval(params['exp_type'])(logger)
    stim.setup()
    stim.prepare()

    # get experiment
    exprmt = stim.get_experiment()(logger, timer, params)

    # RUN
    while logger.get_setup_state() == 'running':
        # # # # # pre-Trial period # # # # #
        cond = stim.init_trial()
        exprmt.pre_trial(cond)

        # # # # # Trial period # # # # #
        timer.start()  # Start countdown for response
        while timer.elapsed_time() < params['trial_duration']*1000 and stim.isrunning:  # response period
            stim.start_trial()  # Start Stimulus
            break_trial = exprmt.trial()  # get appropriate response
            if break_trial: break  # break if experiment calls for it
        stim.stop_trial()  # stop stimulus when timeout

        # # # # # Post-Trial Period # # # # #
        exprmt.post_trial(break_trial)

        # # # # # Intertrial period # # # # #
        timer.start()
        while timer.elapsed_time() < params['intertrial_duration']*1000:
            exprmt.inter_trial()

    # close everything
    logger.update_setup_state('ready')

# stim.close()
sys.exit(0)

