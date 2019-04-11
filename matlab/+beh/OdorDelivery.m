%{
# Odor delivery timestamps
-> beh.Session
time                        : int                           # time from session start (ms)
odor_idx=0                  : int                           # odor number
%}


classdef OdorDelivery < dj.Manual
end