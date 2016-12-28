from Licker import *
from Logger import *
from Stimulus import *
import sys


def runner(animal_id, task_idx):

    # get objects
    timer = Timer()
    logger = Logger()

    # start session
    logger.log_session(animal_id, task_idx)

    # get parameters
    params = (Task & logger.session_key).fetch1()

    # Initialize stimulus
    stim = params.cond_table().prepare(params.conditions)
    stim.init_block()
    logger.log_conditions(stim.get_condition_table)

    # RUN
    while trial < max_trials:  # Each trial is one block

        # new trial
        reward_probe = stim.init_trial()

        # Start countdown for response
        timer.start()
        while timer.elapsed_time() < params.trial_duration:  # response period

            # Show Stimulus
            stim.show_trial()

            if Licker().lick():
                if reward_probe > 0:
                    stim.color([88, 128, 88])
                else:
                    stim.color([128, 88, 88])
                break

        else:  # no lick case
            if reward_probe > 0:
                stim.color([128, 88, 88])
            else:
                stim.color([88, 128, 88])

        stim.stop_trial()
        timer.start()

        # intertrial period
        while timer.elapsed_time() < params.intertrial_duration:
            if Licker().lick():
                timer.start()

        trial += 1

    # close everything
    stim.close()
    quit()

# input parameters
runner(sys.argv[2], sys.argv[3])
