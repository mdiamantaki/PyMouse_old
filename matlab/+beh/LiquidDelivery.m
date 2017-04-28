%{
beh.LiquidDelivery (manual) # Liquid delivery timestamps
-> beh.Session
time            : int                    # time from session start (ms)
---
probe                       : int                           # probe number
%}


classdef LiquidDelivery < dj.Relvar
    
     methods
        function plot(obj,varargin)
            
            params.factor = 1;
            params.color = [0 0 1];
            params = getParams(params,varargin);
            
            times = msec2tmst(fetch(beh.Session & obj),fetchn(obj,'time'));
            plot(times,ones(size(times)) * params.factor,'.','color',params.color)
        end
     end
    
end

