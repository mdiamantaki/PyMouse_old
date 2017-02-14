from Logger import *
from Stimulus import *
import sys

# setup loger
logger = Logger()

# get task
logger.log_setup()
state = 'ready'
while not state == 'running':
    state, animal_id, task_idx = (SetupInfo() & dict(setup=logger.setup)).fetch1['state', 'animal_id', 'task_idx']
    time.sleep(1)

# start session
logger.log_session(animal_id, task_idx)

# get parameters
params = (Task() & dict(task_idx=task_idx)).fetch1()

# prepare stimulus
stim = eval(params['exp_type'])(logger)
stim.setup()
stim.prepare()

# get experiment
timer = Timer()
exprmt = stim.get_experiment()(logger, timer, params)

# RUN
max_trials = 5
trial = 0
while logger.update_setup_state('running'):

    # trial period
    cond = stim.init_trial()
    exprmt.pre_trial(cond)
    timer.start()  # Start countdown for response
    while timer.elapsed_time() < params['trial_duration']*1000 and stim.isrunning:  # response period

        # Start Stimulus
        stim.start_trial()

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

# close everything
logger.update_setup_state('stopped')

# stim.close()
sys.exit(0)

