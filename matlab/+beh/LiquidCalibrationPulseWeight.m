%{
beh.LiquidCalibrationPulseWeight (manual) # Data for volume per pulse duty cycle estimation
-> beh.LiquidCalibration
pulse_dur       : int                    # duration of pulse in ms
---
pulse_num                   : int                           # number of pulses
weight                      : float                         # weight of total liquid released in gr
%}


classdef LiquidCalibrationPulseWeight < dj.Relvar
end


