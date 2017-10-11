
from Logger import *
from Experiment import *

class ExpControl:
    """ This class handles the control of session/stim from 2pmaster"""

    def __init__(self, logger):
        self.timer = None
        self.params = None
        self.exprmt = None
        self.logger = logger

    def do_run_trial(self):
        self.exprmt.pre_trial()

        # # # # # Trial period # # # # #
        self.timer.start()  # Start countdown for response]
        while self.timer.elapsed_time() < self.params['trial_duration'] * 1000:  # response period
            break_trial = self.exprmt.trial()  # get appropriate response
            if break_trial:
                break  # break if experiment calls for it

        # # # # # Post-Trial Period # # # # #
        self.exprmt.post_trial()

        # # # # # Intertrial period # # # # #
        self.timer.start()
        while self.timer.elapsed_time() < self.params['intertrial_duration'] * 1000:
            self.exprmt.inter_trial()

    def do_initialize(self):
        """Initialize the stimulation software"""
        self.logger.update_setup_state('systemReady')

    def do_start_session(self):
        """start stimulation session"""
        self.logger.init_params()  # clear settings from previous session
        self.logger.log_session()  # start session
        self.logger.update_setup_state('sessionRunning')

    def do_start_stim(self):
        """start stimulation trials"""
        self.params = (Task() & dict(task_idx=self.logger.task_idx)).fetch1()  # get parameters
        self.timer = Timer()  # main timer for trials
        self.exprmt = eval(self.params['exp_type'])(self.logger, self.timer, self.params)  # get experiment & init
        self.exprmt.prepare()  # prepare stuff
        self.logger.update_setup_state('stimRunning')
        while self.logger.get_setup_state_control() == 'startStim':
            if self.exprmt.run():
                self.logger.ping()
                self.do_run_trial()
            else:
                time.sleep(0.1)

    def do_stop_stim(self):
        # # # # # Cleanup # # # # #
        if self.logger.get_setup_state == 'stimRunning':
            self.exprmt.cleanup()
            self.logger.update_setup_state('sessionRunning')

    def do_stop_session(self):
        self.do_stop_stim()
        self.logger.update_setup_state('systemReady')

    def process_command(self,command):
        #   process command
        if command == 'Initialize':
            # wait for initialization
            self.do_initialize()
        elif command == 'startSession':
            self.do_start_session()
        elif command == 'startStim':
            self.do_start_stim()  # this is a busy loop
        elif command == 'stopStim':
            self.do_stop_stim()
        elif command == 'stopSession':
            self.do_stop_session()
        else:
            pass
