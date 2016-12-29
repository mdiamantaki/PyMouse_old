from Licker import *
from Logger import *
from Stimulus import *
import sys


def runner(animal_id, task_idx):

    # get objects
    timer = Timer()
    logger = Logger()
    licker = Licker(logger)

    # start session
    logger.log_session(animal_id, task_idx)

    # get parameters
    params = (Task() & logger.get_session_key()).fetch1()

    # Initialize stimulus
    stim = eval(params['exp_type'])(logger)
    condition_indexes = logger.log_conditions(stim.get_condition_table())
    stim.prepare(condition_indexes)


    # RUN
    max_trials = 2
    trial = 0
    while trial < max_trials:  # Each trial is one block

        # new trial
        cond_idx = stim.init_trial()
        logger.start_trial(cond_idx)
        #reward_probe =

        # Start countdown for response
        timer.start()
        while timer.elapsed_time() < params['trial_duration']*1000:  # response period

            # Show Stimulus
            stim.show_trial()

            if licker.lick():
                pass
             #   if reward_probe > 0:
             #       stim.color([88, 128, 88])
             #   else:
             #       stim.color([128, 88, 88])
             #   break

        else:  # no lick case
            pass
            #if reward_probe > 0:
            #    stim.color([128, 88, 88])
            #else:
            #    stim.color([88, 128, 88])

        stim.stop_trial()
        logger.log_trial()
        timer.start()

        # intertrial period
        while timer.elapsed_time() < params['intertrial_duration']*1000:
            if licker.lick():
                timer.start()

        trial += 1

    # close everything
    stim.close()
    quit()

# input parameters
runner(sys.argv[1], sys.argv[2])
