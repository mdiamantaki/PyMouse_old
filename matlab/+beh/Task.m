%{
beh.Task (lookup) # Behavioral experiment parameters
task_idx        : int                    # task identification number
---
-> beh.ExperimentType
-> beh.StimulusType
intertrial_duration=30      : int                           # time in between trials (s)
trial_duration=30           : int                           # trial time (s)
timeout_duration=180        : int                           # timeout punishment delay (s)
airpuff_duration=400        : int                           # duration of positive punishment (ms)
response_interval=1000      : int                           # time before a new lick is considered a valid response (ms)
reward_amount=8             : int                           # microliters of liquid
silence_thr=30              : int                           # lickless period after which stimulus is paused (min)
conditions                  : varchar(4095)                 # stimuli to be presented (array of dictionaries)
description                 : varchar(2048)                 # task description
%}


classdef Task < dj.Relvar
end
