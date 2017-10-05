from Logger import *
from Experiment import *
import sys

logger = PCLogger()                                                     # setup logger & timer
logger.log_setup()                                                    # publish IP and make setup available


# # # # Waiting for instructions loop # # # # #
while not logger.get_setup_state() == 'stopped':

    while logger.get_setup_state() == 'ready':                        # wait for remote start
        time.sleep(1)

    if not logger.get_setup_state() == 'stopped':                     # run experiment unless stopped
        # # # # # Prepare # # # # #
        logger.init_params()  # clear settings from previous session
        logger.log_session()  # start session
        params = (Task() & dict(task_idx=logger.task_idx)).fetch1()  # get parameters
        timer = Timer()  # main timer for trials
        exprmt = eval(params['exp_type'])(logger, timer, params)  # get experiment & init
        exprmt.prepare()  # prepare stuff

        # # # # # Run # # # # #
        while exprmt.run():

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

        # # # # # Cleanup # # # # #
        exprmt.cleanup()
        logger.update_setup_state('ready')                            # update setup state

# # # # # Exit # # # # #
sys.exit(0)


