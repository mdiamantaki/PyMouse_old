%{
beh.Session (manual) # Behavior session info
animal_id       : int                    # animal id
session_id      : smallint               # session number
---
intertrial_duration         : int                           # time in between trials (s)
trial_duration              : int                           # trial time (s)
timeout_duration            : int                           # timeout punishment delay (s)
airpuff_duration            : int                           # duration of positive punishment (ms)
response_interval           : int                           # time before a new lick is considered a valid response (ms)
reward_amount               : int                           # microliters of liquid
setup                       : varchar(256)                  # computer id
session_tmst=CURRENT_TIMESTAMP: timestamp                   # session timestamp
notes                       : varchar(2048)                 # session notes
%}


classdef Session < dj.Relvar
    
    methods
        function plot(obj)
            figure
            plot(beh.Lick & obj,'color',[0 0 0])
            hold on
            plot(beh.Trial & obj,'factor',2,'color',[0 0 0.5])
            plot(beh.Trial & obj,'factor',1.9,'color',[0.5 0.5 1],'time','end_time')
            plot(beh.LiquidDelivery & obj,'factor',1.5,'color',[0 1 0])
            plot(beh.AirpuffDelivery & obj,'factor',1.4,'color',[1 0 0])
            ylim([-2 8])
            set(gca,'box','off','ycolor',[1 1 1],'ytick',[])
            l = legend('Licks','Trial Start','Trial End','Liquid','Air');
            set(l,'box','off')
        end
    end
    
end