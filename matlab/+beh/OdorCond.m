%{
# reward probe conditions
-> beh.Condition
---
odor_dur=1000               : int                           # odor duration (ms)
odor_idx=0                  : int                           # odor index for channel mapping
odor_name                   : varchar(255)                  # name of the odor
%}


classdef OdorCond < dj.Manual
end