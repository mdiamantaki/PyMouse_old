from Logger import *
from Experiment import *
import sys

logg = RPLogger()                                                     # setup logger & timer
logg.log_setup()                                                    # publish IP and make setup available


def train(logger=logg):
    """ Run training experiment """

    # # # # # Prepare # # # # #
    logger.init_params()                                            # clear settings from previous session
    logger.log_session()                                            # start session
    params = (Task() & dict(task_idx=logger.task_idx)).fetch1()     # get parameters
    timer = Timer()                                                 # main timer for trials
    exprmt = eval(params['exp_type'])(logger, timer, params)        # get experiment & init
    exprmt.prepare()                                                # prepare stuff

    # # # # # Run # # # # #
    while exprmt.run():

        # # # # # Pre-Trial period # # # # #
        exprmt.pre_trial()

        # # # # # Trial period # # # # #
        timer.start()                                                # Start countdown for response
        while timer.elapsed_time() < params['trial_duration']*1000:  # response period
            break_trial = exprmt.trial()                             # get appropriate response
            if break_trial:
                break                                                # break if experiment calls for it

        # # # # # Post-Trial Period # # # # #
        exprmt.post_trial()

        # # # # # Intertrial period # # # # #
        timer.start()
        while timer.elapsed_time() < params['intertrial_duration']*1000:
            exprmt.inter_trial()

    # # # # # Cleanup # # # # #
    exprmt.cleanup()


def calibrate(logger=logg):
    """ Lickspout liquid delivery calibration """
    task_idx = (SetupInfo() & dict(setup=logger.setup)).fetch1['task_idx']
    duration, probes, pulsenum, pulse_interval, save = \
        (CalibrationTask() & dict(task_idx=task_idx)).fetch1[
            'pulse_dur', 'probe', 'pulse_num', 'pulse_interval', 'save']
    probes = eval(probes)
    valve = ValveControl(logger)                                    # get valve object
    print('Running calibration')
    pulse = 0
    stim = Stimulus(logger)
    stim.setup()
    font = pygame.font.SysFont("comicsansms", 100)
    while pulse < pulsenum:
        text = font.render('Pulse %d/%d' % (pulse + 1, pulsenum), True, (0, 128, 0))
        stim.screen.fill((255, 255, 255))
        stim.screen.blit(text, (stim.size[1]/4, stim.size[1]/2))
        stim.flip()
        for probe in probes:
            valve.give_liquid(probe, duration, False)               # release liquid
        time.sleep(duration / 1000 + pulse_interval / 1000)         # wait for next pulse
        pulse += 1                                                  # update trial
    if save == 'yes':
        for probe in probes:
            logger.log_pulse_weight(duration, probe, pulsenum)      # insert
    stim.screen.fill((255, 255, 255))
    stim.screen.blit(font.render('Done calibrating', True, (0, 128, 0)), (stim.size[1]/4, stim.size[1]/2))
    stim.flip()

# # # # Waiting for instructions loop # # # # #
while not logg.get_setup_state() == 'stopped':
    while logg.get_setup_state() == 'ready':                        # wait for remote start
        time.sleep(1)
    if not logg.get_setup_state() == 'stopped':                     # run experiment unless stopped
        #try:
        eval(logg.get_setup_task())(logg)
        logg.update_setup_state('ready')                            # update setup state
        #except:
        #    print("Unexpected error:", sys.exc_info()[0])
        #    logg.update_setup_state('stopped', sys.exc_info()[0])

# # # # # Exit # # # # #
sys.exit(0)


