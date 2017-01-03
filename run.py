from Licker import *
from Logger import *
from Stimulus import *
import sys


def runner(animal_id, task_idx):

    # start session
    logger = Logger()
    logger.log_session(animal_id, task_idx)

    # get parameters
    params = (Task() & dict(task_idx=task_idx)).fetch1()

    # Start stimulus
    stim = eval(params['exp_type'])(logger)
    stim.prepare()

    # get objects
    timer = Timer()
    licker = Licker(logger, params['response_interval'])
    resp = stim.get_responder()(logger, timer, params)

    # RUN
    max_trials = 2
    trial = 0
    while trial < max_trials:

        # trial period
        cond = stim.init_trial()
        resp.prepare_response(cond)
        timer.start()  # Start countdown for response
        while timer.elapsed_time() < params['trial_duration']*1000 and stim.isrunning:  # response period

            # Show Stimulus
            stim.show_trial()

            # Check for licks
            probe = licker.lick()
            if probe > 0:
                # appropriate response to a lick (reward/punish/break trial)
                break_trial = resp.trial_lick(probe)
                if break_trial:
                    break

        else:  # appropriate response to a no lick case
            resp.trial_no_lick()

        # stop stimulus when timeout
        stim.stop_trial()

        # intertrial period
        timer.start()
        while timer.elapsed_time() < params['intertrial_duration']*1000:
            probe = licker.lick()
            if probe > 0:
                resp.inter_trial_lick(probe)
        else:
            resp.inter_trial_no_lick()

        # in case of an unresponsive animal add a pause
        if licker.minutessincelastlick() > params['silence_thr'] > 0:
            print('Sleeping...')
            while licker.lick() == 0:
                pass

        # update trial
        trial += 1

    # close everything
    # stim.close()
    sys.exit(0)

# input parameters
runner(sys.argv[1], sys.argv[2])