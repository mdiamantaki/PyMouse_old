import numpy
import socket
from Behavior import *
from itertools import product


class Logger:
    """ This class handles the database logging"""

    def __init__(self):
        self.session_key = dict()
        self.param_table = []
        self.condition_table = []
        self.last_trial = 0
        self.conditions = []

    def log_session(self, animal_id, task_idx):

        self.session_key['animal_id'] = animal_id

        last_sessions = (Session() & self.session_key).fetch['session_id']
        if numpy.size(last_sessions) == 0:
            last_session = 0
        else:
            last_session = numpy.max(last_sessions)

        self.session_key['session_id'] = last_session + 1

        task_fields = set(Session().heading.names).intersection(Task().heading.names)
        task_params = (Task() & dict(task_idx=task_idx)).proj(*task_fields).fetch1()
        del task_params['task_idx']
        key = dict(self.session_key.items() | task_params.items())
        key['setup'] = socket.gethostname()

        Session().insert1(key)

    def log_conditions(self, condition_table):

        last_conds = (Condition() & self.session_key).fetch['cond_idx']
        if numpy.size(last_conds) == 0:
            last_cond = 0
        else:
            last_cond = numpy.max(last_conds)

        # generate factorial conditions
        conditions = eval((Task() & self.session_key).fetch1['conditions'])
        conditions = list((dict(zip(conditions, x)) for x in product(*conditions.values())))

        cond_idx = last_cond

        for cond in conditions:
            cond_idx += 1
            Condition().insert1(dict(self.session_key, cond_idx=cond_idx))
            if 'probe' in cond:
                RewardCond().insert1(dict(self.session_key,
                                          cond_idx=cond_idx,
                                          probe=cond.pop('probe')))
            condition_table().insert1(dict(cond.items() | self.session_key.items(), cond_idx=cond_idx))

    def log_trial(self, cond_idx, start_time, end_time):

        trial_key = dict(self.session_key,
                         trial_idx=self.last_trial+1,
                         cond_idx=cond_idx,
                         start_time=start_time,
                         end_time=end_time)
        Trial().insert(trial_key)

        self.last_trial += 1

    def log_reward(self, timestamp):
        LiquidDelivery().insert(dict(self.session_key, time=timestamp))

    def log_lick(self, timestamp):
        Lick().insert(dict(self.session_key, time=timestamp))

    def log_air(self, timestamp):
        AirpuffDelivery().insert(dict(self.session_key, time=timestamp))





