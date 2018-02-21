import numpy, socket
from Timer import *
from Database import *
from itertools import product
from queue import Queue
import time as systime
import datetime
#from threading import Thread


class Logger:
    """ This class handles the database logging"""

    def __init__(self):
        self.session_key = dict()
        self.setup = socket.gethostname()
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        self.ip = s.getsockname()[0]
        print(self.ip)
        self.init_params()
        #self.thread = Thread(target=self.inserter)
        #self.thread.daemon = True
        #self.thread.start()

    def init_params(self):
        self.last_trial = 0
        self.queue = Queue()
        self.timer = Timer()
        self.trial_start = 0
        self.curr_cond = []
        self.task_idx = []
        self.reward_amount = []

    def log_session(self):
        """Logs session"""
        pass

    def log_conditions(self, condition_table):
        """Logs conditions"""
        pass

    def start_trial(self, cond_idx):
        self.trial_start = self.timer.elapsed_time()

    def log_trial(self, last_flip_count=0):
        """Log experiment trial"""
        pass

    def log_setup(self):
        """Log setup information"""
        pass

    def update_setup_state(self, state):
        pass

    def get_setup_state(self):
        pass

    def get_setup_task(self):
        pass

    def get_session_key(self):
        return self.session_key

    def ping(self):
        """update timestamp"""
        pass

    def inserter(self):  # insert worker, in case we need threading
        while not self.queue.empty():
            item = self.queue.get()
            item['table'].insert1(item['tuple'])


class RPLogger(Logger):
    """ This class handles the database logging for Raspberry pi"""

    def init_params(self):
        self.last_trial = 0
        self.queue = Queue()
        self.timer = Timer()
        self.trial_start = 0
        self.curr_cond = []
        self.task_idx = []
        self.reward_amount = []

    def log_session(self):

        animal_id, task_idx = (SetupInfo() & dict(setup=self.setup)).fetch1('animal_id', 'task_idx')
        self.task_idx = task_idx

        # create session key
        self.session_key['animal_id'] = animal_id
        last_sessions = (Session() & self.session_key).fetch('session_id')
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
        self.reward_amount = task_params['reward_amount']/1000  # convert to ml

        # start session time
        self.timer.start()
        self.inserter()

    def log_conditions(self, condition_table):

        # generate factorial conditions
        conditions = eval((Task() & dict(task_idx=self.task_idx)).fetch1('conditions'))
        conditions = sum([list((dict(zip(conds, x)) for x in product(*conds.values()))) for conds in conditions], [])

        # iterate through all conditions and insert
        cond_idx = 0
        probes = numpy.empty(numpy.size(conditions))
        for cond in conditions:
            cond_idx += 1
            self.queue.put(dict(table=Condition(), tuple=dict(self.session_key, cond_idx=cond_idx)))
            if 'probe' in cond:
                probes[cond_idx-1] = cond.pop('probe')
                self.queue.put(dict(table=RewardCond(), tuple=dict(self.session_key,
                                                                   cond_idx=cond_idx,
                                                                   probe=probes[cond_idx-1])))
            self.queue.put(dict(table=condition_table(), tuple=dict(cond.items() | self.session_key.items(),
                                                                    cond_idx=cond_idx)))
        self.inserter()

        # outputs all the condition indexes of the session
        cond_indexes = list(range(1, cond_idx + 1))  # assumes continuous & complete indexes for each session
        return numpy.array(cond_indexes), numpy.array(probes)

    def start_trial(self, cond_idx):
        self.curr_cond = cond_idx
        self.trial_start = self.timer.elapsed_time()

        # return condition key
        return dict(self.session_key, cond_idx=cond_idx)

    def log_trial(self, last_flip_count=0):
        timestamp = self.timer.elapsed_time()
        trial_key = dict(self.session_key,
                         trial_idx=self.last_trial+1,
                         cond_idx=self.curr_cond,
                         start_time=self.trial_start,
                         end_time=timestamp,
                         last_flip_count=last_flip_count)
        self.queue.put(dict(table=Trial(), tuple=trial_key))
        self.last_trial += 1
        self.inserter()

        # insert ping
        self.ping()

    def log_liquid(self, probe):
        timestamp = self.timer.elapsed_time()
        self.queue.put(dict(table=LiquidDelivery(), tuple=dict(self.session_key, time=timestamp, probe=probe)))
        self.inserter()

    def log_odor(self, odor_idx):
        timestamp = self.timer.elapsed_time()
        self.queue.put(dict(table=OdorDelivery(), tuple=dict(self.session_key, time=timestamp, odor_idx=odor_idx)))
        self.inserter()

    def log_lick(self, probe):
        timestamp = self.timer.elapsed_time()
        self.queue.put(dict(table=Lick(), tuple=dict(self.session_key,
                                                     time=timestamp,
                                                     probe=probe)))
        #self.inserter()

    def log_air(self, probe):
        timestamp = self.timer.elapsed_time()
        self.queue.put(dict(table=AirpuffDelivery(), tuple=dict(self.session_key, time=timestamp, probe=probe)))
        self.inserter()

    def log_pulse_weight(self, pulse_dur, probe, pulse_num, weight=0):
        cal_key = dict(setup=self.setup, probe=probe, date=systime.strftime("%Y-%m-%d"))
        LiquidCalibration().insert1(cal_key, skip_duplicates=True)
        (LiquidCalibration.PulseWeight() & dict(cal_key, pulse_dur=pulse_dur)).delete_quick()
        LiquidCalibration.PulseWeight().insert1(dict(cal_key,
                                                     pulse_dur=pulse_dur,
                                                     pulse_num=pulse_num,
                                                     weight=weight))

    def log_setup(self):
        key = dict(setup=self.setup)

        # update values in case they exist
        if numpy.size((SetupInfo() & dict(setup=self.setup)).fetch()):
            key = (SetupInfo() & dict(setup=self.setup)).fetch1()
            (SetupInfo() & dict(setup=self.setup)).delete_quick()

        # insert new setup
        key['ip'] = self.ip
        key['state'] = 'ready'
        SetupInfo().insert1(key)

    def update_setup_state(self, state):
        key = (SetupInfo() & dict(setup=self.setup)).fetch1()
        in_state = key['state'] == state
        if not in_state:
            (SetupInfo() & dict(setup=self.setup))._update('state', state)
        return in_state

    def get_setup_state(self):
        state = (SetupInfo() & dict(setup=self.setup)).fetch1('state')
        return state

    def get_setup_task(self):
        task = (SetupInfo() & dict(setup=self.setup)).fetch1('task')
        return task

    def get_session_key(self):
        return self.session_key

    def ping(self):
        if numpy.size((SetupInfo() & dict(setup=self.setup)).fetch()):
            lp = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            (SetupInfo() & dict(setup=self.setup))._update('last_ping', lp)


class PCLogger(Logger):
    """ This class handles the database logging for 2P systems"""
    def init_params(self):
        self.queue = Queue()
        self.timer = Timer()
        self.task_idx = []
        self.last_time = systime.time()
        self.trial_idx = []

    def log_session(self):
        animal_id, session, task_idx = (SetupControl() & dict(setup=self.setup)).fetch1('animal_id', 'session', 'task_idx')

        self.task_idx = task_idx

        # create session key
        self.session_key['animal_id'] = animal_id
        self.session_key['session_id'] = session

        # get task parameters for session table
        if numpy.size((Session() & self.session_key).fetch()):  # if session exists
            self.reward_amount = (Session() & self.session_key).fetch1('reward_amount')/1000
        else:
            task_fields = set(Session().heading.names).intersection(Task().heading.names)
            task_params = (Task() & dict(task_idx=task_idx)).proj(*task_fields).fetch1()
            del task_params['task_idx']
            key = dict(self.session_key.items() | task_params.items())
            key['setup'] = self.setup
            self.queue.put(dict(table=Session(), tuple=key))
            self.reward_amount = task_params['reward_amount']/1000  # convert to ml

        # start session time
        self.timer.start()
        self.inserter()

    def update_setup_state(self, state):
        key = (SetupControl() & dict(setup=self.setup)).fetch1()
        in_state = key['state'] == state
        if not in_state:
            (SetupControl() & dict(setup=self.setup))._update('state', state)

    def get_setup_state(self):
        state = (SetupControl() & dict(setup=self.setup)).fetch1('state')
        return state

    def get_setup_state_control(self):
        state = (SetupControl() & dict(setup=self.setup)).fetch1('state_control')
        return state

    def get_setup_task(self):
        task = (SetupControl() & dict(setup=self.setup)).fetch1('task')
        return task

    def get_stimulus(self):
        task = (SetupControl() & dict(setup=self.setup)).fetch1('stimulus')
        return task

    def get_experimenter(self):
        task = (SetupControl() & dict(setup=self.setup)).fetch1('experimenter')
        return task

    def setup_experiment_schema(self):
        self.experiment = dj.create_virtual_module('experiment', 'pipeline_experiment')

    def ping(self):
        nw = systime.time()
        if nw-self.last_time > 1:
            lp = format(datetime.datetime.now(),"%Y-%m-%d %H:%M:%S")
            (SetupControl() & dict(setup=self.setup))._update('last_ping', lp)
            self.last_time = nw

    def get_scan_key(self):
        animal_id = (SetupControl() & dict(setup=self.setup)).fetch1('animal_id')
        session = (SetupControl() & dict(setup=self.setup)).fetch1('session')
        scan_idx = (SetupControl() & dict(setup=self.setup)).fetch1('scan_idx')
        return dict(animal_id=animal_id, session=session, scan_idx=scan_idx)

    def get_trial_key(self):
        animal_id = (SetupControl() & dict(setup=self.setup)).fetch1('animal_id')
        session = (SetupControl() & dict(setup=self.setup)).fetch1('session')
        scan_idx = (SetupControl() & dict(setup=self.setup)).fetch1('scan_idx')
        return dict(animal_id=animal_id, session=session, scan_idx=scan_idx, trial_idx=self.trial_idx)

    def get_protocol_file(self):
        protocol_table = self.experiment.VisProtocol()
        tp = protocol_table & dict(vis_protocol=self.get_stimulus(),username=self.get_experimenter())
        return tp.fetch1('vis_filename')

    def update_next_trial(self, next_trial):
        (SetupControl() & dict(setup=self.setup))._update('next_trial', next_trial)
        self.trial_idx = next_trial
