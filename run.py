from Logger import *
from Stimulus import *
import sys


def runner(animal_id, task_idx):
    """ Main experiment runner"""

    # start session
    logger = Logger()
    logger.log_session(animal_id, task_idx)

    # get parameters
    params = (Task() & dict(task_idx=task_idx)).fetch1()

    # Start stimulus
    stim = eval(params['exp_type'])(logger)
    stim.setup()
    stim.prepare()

    # get experiment
    timer = Timer()
    exprmt = stim.get_experiment()(logger, timer, params)

    # RUN
    max_trials = 5
    trial = 0
    while trial < max_trials:

        # trial period
        cond = stim.init_trial()
        exprmt.pre_trial(cond)
        timer.start()  # Start countdown for response
        while timer.elapsed_time() < params['trial_duration']*1000 and stim.isrunning:  # response period

            # Show Stimulus
            stim.show_trial()

            # get appropriate response
            break_trial = exprmt.trial()
            if break_trial:
                break

        # stop stimulus when timeout
        stim.stop_trial()

        # do stuff after trial ends
        exprmt.post_trial(break_trial)

        # intertrial period
        timer.start()
        while timer.elapsed_time() < params['intertrial_duration']*1000:
            exprmt.inter_trial()

        # update trial
        trial += 1

    # close everything
    # stim.close()
    sys.exit(0)

# input parameters
runner(sys.argv[1], sys.argv[2])