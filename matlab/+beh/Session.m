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
        function plot(self)
            figure
            plot(beh.Lick & self,'color',[0 0 0],'factor',2.01)
            hold on
            plot(beh.Trial & self,'factor',2,'color',[0 0 1])
            plot(beh.Trial & self,'factor',1.9,'color',[0.5 0.5 1],'time','end_time')
            plot(beh.LiquidDelivery & self,'factor',1.5,'color',[0 1 0])
            plot(beh.AirpuffDelivery & self,'factor',1.4,'color',[1 0 0])
            ylim([-2 8])
            set(gca,'box','off','ycolor',[1 1 1],'ytick',[])
            l = legend('Licks','Trial Start','pretrial','Trial End','Liquid','Air');
            set(l,'box','off')
        end
        
        function latest_session = getLatest(self,restrict)
            
            if nargin<2
                restrict = 'now';
            end

            [mice,state] = fetchn(proj(beh.SetupInfo,'animal_id','state') & self & 'animal_id>0','animal_id','state');
            
            keys = [];
            for imouse=1:length(mice)
                keys(imouse).animal_id = mice(imouse);
                k.animal_id = mice(imouse);
                sessions = fetch(self & k ,'ORDER BY session_id DESC');
                if  strcmp(restrict,'now') || ~strcmp(state{imouse},'running')
                    sess_idx = 1;
                else
                    sess_idx = 2;
                end

                keys(imouse).session_id = sessions(sess_idx).session_id;
            end
            latest_session = self & keys;

        end
        
        function tmst = msec2tmst(self, msec_since_session_start)

            msec2days = @(x) x/1000/60/60/24;

            sess_tmst = fetch1(self,'session_tmst');
            sess_tmst = datenum(sess_tmst,'yyyy-mm-dd HH:MM:SS');
            tmst = (msec2days(msec_since_session_start) + sess_tmst);
        end
    end
    
end