%{
beh.CalibrationTask (lookup) # Calibration parameters
task_idx        : int                    # task identification number
---
probe                       : int                           # probe number
pulse_dur                   : int                           # duration of pulse in ms
pulse_num                   : int                           # number of pulses
pulse_interval              : int                           # interval between pulses in ms
%}


classdef CalibrationTask < dj.Relvar
end
