from Logger import *
from Experiment import *
from ExpControl import *

logger = PCLogger()                                                     # setup logger & timer
logger.log_setup()                                                    # publish IP and make setup available
ec = ExpControl(logger)

# # # # Waiting for instructions loop # # # # #
ec.do_initialize()  # initialize
systime.sleep(3)  # wait for 2pmaster to establish db connection and initialize
while True:

    cmd = logger.get_setup_state_control()
    ec.process_command(cmd)
    systime.sleep(0.1)

