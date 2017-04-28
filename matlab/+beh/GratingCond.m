%{
beh.GratingCond (manual) # Orientation gratings conditions
-> beh.Condition
---
direction                   : int                           # in degrees (0-360)
spatial_period              : int                           # pixels/cycle
temporal_freq               : float                         # cycles/sec
contrast=100                : int                           # 0-100 Michelson contrast
phase=0                     : float                         # initial phase in rad
%}


classdef GratingCond < dj.Relvar
end
