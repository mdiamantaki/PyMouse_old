import numpy, socket
from queue import Queue
from Behavior import *
from itertools import product
from threading import Thread
from Timer import *


class Logger:
    """ This class handles the database logging"""

    def __init__(self):
        self.session_key = dict()
        self.last_trial = 0
        self.queue = Queue()
        self.thread = Thread(target=self.inserter)
        self.thread.daemon = True
        self.thread.start()
        self.timer = Timer()
        self.trial_start = 0
        self.curr_cond = []

    def log_session(self, animal_id, task_idx):
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
        key['setup'] = socket.gethostname()
        self.queue.put(dict(table=Session(), tuple=key))

        # start session time
        self.timer.start()

    def log_conditions(self, condition_table):
        # get last condition for this session
        last_conds = (Condition() & self.session_key).fetch['cond_idx']
        if numpy.size(last_conds) == 0:
            cond_idx = 0
        else:
            cond_idx = numpy.max(last_conds)

        # generate factorial conditions
        conditions = eval((Task() & self.session_key).fetch1['conditions'])
        conditions = list((dict(zip(conditions, x)) for x in product(*conditions.values())))

        # iterate through all conditions and insert
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
        cond_indexes = (Condition() & self.session_key).fetch['cond_idx']
        return cond_indexes

    def start_trial(self, cond_idx):
        self.curr_cond = cond_idx
        self.trial_start = self.timer.elapsed_time()

    def log_trial(self):
        timestamp = self.timer.elapsed_time()
        trial_key = dict(self.session_key,
                         trial_idx=self.last_trial+1,
                         cond_idx=self.curr_cond,
                         start_time=self.trial_start,
                         end_time=timestamp)
        self.queue.put(dict(table=Trial(), tuple=trial_key))
        self.last_trial += 1

    def log_reward(self):
        timestamp = self.timer.elapsed_time()
        self.queue.put(dict(table=LiquidDelivery(), tuple=dict(self.session_key, time=timestamp)))

    def log_lick(self):
        timestamp = self.timer.elapsed_time()
        self.queue.put(dict(table=Lick(), tuple=dict(self.session_key, time=timestamp)))

    def log_air(self):
        timestamp = self.timer.elapsed_time()
        self.queue.put(dict(table=AirpuffDelivery(), tuple=dict(self.session_key, time=timestamp)))

    def get_session_key(self):
        return self.session_key

    def inserter(self):  # insert worker
        while True:
            if self.queue.qsize() > 0:
                item = self.queue.get()
                item['table'].insert1(item['tuple'])
                self.queue.task_done()






