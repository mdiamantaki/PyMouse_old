from time import time


class Timer:
    """ This is a timer that is used for the state system
    """

    def __init__(self):
        self.start_time = 0
        self.time = time

    def start(self):
        self.start_time = self.time()

    def elapsed_time(self):
        return self.time() - self.start_time
