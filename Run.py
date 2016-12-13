from Timer import *
from Licker import *
from Stimulus import *
import numpy as np
import pygame
import os
from glob import glob

os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0, 0)
timer = Timer()

# Set Parameters
w = 480
h = 320
max_trials = 1
RP = 4
ITI = 2

# Set images
GO_images = glob('object3d/obj1*')
NOGO_images = glob('object3d/obj2*')

# Initialize image matrices
GO_resp = np.ones(np.size(GO_images))
NOGO_resp = np.zeros(np.size(NOGO_images))
ALL_images = GO_images + NOGO_images
ALL_resp = np.concatenate([GO_resp, NOGO_resp])

# Load images
stim = vstimulus(ALL_images, w, h)

# Initialize other settings
timer.start()
stim.init_block()
trial = 0
state_time = 0
pygame.mouse.set_visible(0)

# RUN
while trial < max_trials:  # Each trial is one block

    for istim in range(stim.block_sz):
        index = stim.init_trial()
        corr_resp = ALL_resp[index] == 1

        # Start countdown for response
        timer.start()
        while timer.elapsed_time() < RP:  # response period

            # Show Stimulus
            stim.show()

            events = pygame.event.get()
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    stim.close()
                    quit()

            if Licker().lick():
                print('Correct!' if corr_resp else 'Wrong')
                if corr_resp:
                    stim.color([88, 128, 88])
                else:
                    stim.color([128, 88, 88])

                break
        else:  # no lick case
            print('Wrong!' if corr_resp else 'Correct!')
            if corr_resp:
                stim.color([128, 88, 88])
            else:
                stim.color([88, 128, 88])
        stim.unshow()
        timer.start()
        while timer.elapsed_time() < ITI:
            if Licker().lick():
                timer.start()
                print('wait!')
                stim.color([88, 88, 88])
                stim.unshow()

    trial += 1

# close everything
stim.close()
quit()
