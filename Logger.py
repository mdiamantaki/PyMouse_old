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

        last_sessions = (self.Session() & self.session_key).fetch['session_id']
        if last_sessions.size() == 0:
            last_session = 0
        else:
            last_session = numpy.max(last_sessions)

        self.session_key['session_id'] = last_session + 1
        task_fields = set(Session().heading.names).intersection(Task().heading.names)
        task_params = (Task() & dict(task_idx=task_idx)).proj(*task_fields).fetch1()
        del task_params['task_idx']
        self.session_key = dict(self.session_key.items() | task_params.items())
        self.session_key['setup'] = socket.gethostname()

        Session().insert(self.session_key)

    def log_conditions(self, param_table):

        last_conds = (self.condTable & self.session_key).fetch['cond_idx']
        if last_conds.size() == 0:
            last_cond = 0
        else:
            last_cond = numpy.max(last_conds)

        # generage factorial conditions
        conditions = (Task() & self.session_key).fetch1['conditions']
        conditions = list((dict(zip(conditions, x)) for x in product(*conditions.values())))

        self.currentConditions = []
        for iCond in range(conditions.count()):
            conditions(iCond).cond_idx = iCond + last_cond
            #self.currentConditions = [self.currentConditions condIdx]
            tuple = self.session_key
            #tuple.cond_idx = condIdx
            self.condTable.insert(tuple)
            #paramTable.insert

    def log_trial(self, start_time, end_time):

        trial_key = dict(self.session_key,
                         trial_idx=self.last_trial+1,
                         start_time=start_time,
                         end_time=end_time)
        Trial().insert(trial_key)

        self.last_trial += 1




