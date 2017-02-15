from Logger import *
from Stimulus import *
import sys

# setup loger & timer
logg = Logger()
logg.log_setup()  # publish IP and make setup available


def train(logger=logg):
    # start session
    logger.log_session()

    # get parameters
    params = (Task() & dict(task_idx=logger.task_idx)).fetch1()

    # prepare stimulus
    stim = eval(params['exp_type'])(logger)
    stim.setup()
    stim.prepare()

    # get experiment
    timer = Timer()  # main timer for trials
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

    # update setup state
    logger.update_setup_state('ready')


def calibrate(logger=logg):
    """ LickSpout calibration runner"""
    task_idx = (SetupInfo() & dict(setup=logger.setup)).fetch1['task_idx']
    duration, probe, pulsenum, pulse_interval = \
        (CalibrationTask() & dict(task_idx=task_idx)).fetch1['pulse_dur', 'probe', 'pulse_num', 'pulse_interval']
    valve = ValveControl(logger)  # get valve object
    print('Running calibration')
    trial = 0
    while trial < pulsenum:
        print('Pulse %d/%d' % (trial+1, pulsenum), end="\r", flush=True)
        valve.give_liquid(probe, duration, False)  # release liquid
        time.sleep(duration/1000 + pulse_interval/1000)  # wait for next pulse
        trial += 1  # update trial
    logger.log_pulse_weight(duration, probe, pulsenum)  # insert


while not logg.get_setup_state() == 'stopped':
    # wait for remote start
    while logg.get_setup_state() == 'ready':
        time.sleep(1)

    # run experiment unless stopped
    if not logg.get_setup_state() == 'stopped':
        eval(logg.get_setup_task())(logg)
        logg.update_setup_state('ready')  # update setup state

# close everything
sys.exit(0)


