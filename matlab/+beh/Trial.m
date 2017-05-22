%{
beh.Trial (manual) # Trial information
-> beh.Session
-> beh.Condition
trial_idx       : smallint               # unique condition index
---
start_time                  : int                           # start time from session start (ms)
end_time                    : int                           # end time from session start (ms)
last_flip_count             : int                           # the last flip number in this trial
%}


classdef Trial < dj.Relvar
    methods
        function plot(obj,varargin)
            
            params.factor = 1;
            params.color = [0 0 1];
            params.time = 'start_time';
            params = getParams(params,varargin);
            
            times = msec2tmst(fetch(beh.Session & obj),fetchn(obj, params.time));
            plot(times,ones(size(times))* params.factor,'.','color',params.color)
            
            if strcmp(params.time,'start_time')
                times = msec2tmst(fetch(beh.Session & obj),fetchn(obj, params.time)-30000);
                plot(times,ones(size(times))* params.factor,'.','color',[0.9 0.9 .9])
            end
        end
    end
end
