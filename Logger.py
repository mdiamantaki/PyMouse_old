import numpy, socket
from Timer import *
from Database import *
from itertools import product
from queue import Queue
import time as systime


class Logger:
    """ This class handles the database logging"""

    def __init__(self):
        self.session_key = dict()
        self.setup = socket.gethostname()
        self.last_trial = 0
        self.queue = Queue()
        self.timer = Timer()
        self.trial_start = 0
        self.curr_cond = []
        self.task_idx = []
        self.date = systime.strftime("%Y-%m-%d")

    def log_session(self, animal_id, task_idx):

        self.task_idx = task_idx

        # create session key
        self.session_key['animal_id'] = animal_id
        last_sessions = (Session() & self.session_key).fetch['session_id']
        if numpy.size(last_sessions) == 0:
            last_session = 0
        else:
            last_session = numpy.max(last_sessions)
        self.session_key['session_id'] = last_session + 1

        # get task parameters for session table
        task_fields = set(Session().heading.names).intersection(Task().heading.names)
        task_params = (Task() & dict(task_idx=task_idx)).proj(*task_fields).fetch1()
        del task_params['task_idx']
        key = dict(self.session_key.items() | task_params.items())
        key['setup'] = self.setup
        self.queue.put(dict(table=Session(), tuple=key))

        # start session time
        self.timer.start()
        self.inserter()

    def log_conditions(self, condition_table):

        # generate factorial conditions
        conditions = eval((Task() & self.task_idx).fetch1['conditions'])
        conditions = sum([list((dict(zip(conds, x)) for x in product(*conds.values()))) for conds in conditions], [])

        # iterate through all conditions and insert
        cond_idx = 0
        for cond in conditions:
            cond_idx += 1
            self.queue.put(dict(table=Condition(), tuple=dict(self.session_key, cond_idx=cond_idx)))
            if 'probe' in cond:
                self.queue.put(dict(table=RewardCond(), tuple=dict(self.session_key,
                                                                   cond_idx=cond_idx,
                                                                   probe=cond.pop('probe'))))
            self.queue.put(dict(table=condition_table(), tuple=dict(cond.items() | self.session_key.items(),
                                                                    cond_idx=cond_idx)))
        # outputs all the condition indexes of the session
        cond_indexes = list(range(1, cond_idx+1))  # assumes continuous & complete indexes for each session

        self.inserter()

        return cond_indexes

    def start_trial(self, cond_idx):
        self.curr_cond = cond_idx
        self.trial_start = self.timer.elapsed_time()

        # return condition key
        return dict(self.session_key, cond_idx=cond_idx)

    def log_trial(self):
        timestamp = self.timer.elapsed_time()
        trial_key = dict(self.session_key,
                         trial_idx=self.last_trial+1,
                         cond_idx=self.curr_cond,
                         start_time=self.trial_start,
                         end_time=timestamp)
        self.queue.put(dict(table=Trial(), tuple=trial_key))
        self.last_trial += 1
        self.inserter()

    def log_liquid(self):
        timestamp = self.timer.elapsed_time()
        self.queue.put(dict(table=LiquidDelivery(), tuple=dict(self.session_key, time=timestamp)))
        self.inserter()

    def log_lick(self, probe):
        timestamp = self.timer.elapsed_time()
        self.queue.put(dict(table=Lick(), tuple=dict(self.session_key,
                                                     time=timestamp,
                                                     probe=probe)))
        self.inserter()

    def log_air(self):
        timestamp = self.timer.elapsed_time()
        self.queue.put(dict(table=AirpuffDelivery(), tuple=dict(self.session_key, time=timestamp)))
        self.inserter()

    def log_pulse_weight(self, pulse_dur, probe, pulse_num, weight):
        cal_key = dict(setup=self.setup, probe=probe, date=self.date)
        LiquidCalibration().insert1(cal_key, skip_duplicates=True)
        (LiquidCalibration.PulseWeight() & dict(cal_key, pulse_dur=pulse_dur)).delete_quick()
        LiquidCalibration.PulseWeight().insert1(dict(cal_key,
                                                     pulse_dur=pulse_dur,
                                                     pulse_num=pulse_num,
                                                     weight=weight))

    def get_session_key(self):
        return self.session_key

    def inserter(self):  # insert worker, in case we need threading
        while not self.queue.empty():
            item = self.queue.get()
            item['table'].insert1(item['tuple'])







