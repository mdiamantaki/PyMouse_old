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
        function plot(self,varargin)
            
            params.factor = 1;
            params.color = [0 0 1];
            params.time = 'start_time';
            params = getParams(params,varargin);
            
            times = msec2tmst(fetch(beh.Session & self),fetchn(self, params.time));
            plot(times,ones(size(times))* params.factor,'.','color',params.color)
            
            if strcmp(params.time,'start_time')
                times = msec2tmst(fetch(beh.Session & self),fetchn(self, params.time)-30000);
                plot(times,ones(size(times))* params.factor,'.','color',[0.9 0.9 .9])
            end
        end
        
        function plotN(self)
            mice = unique(fetchn(self & 'animal_id>0','animal_id'));

            figure
            for imouse = 1:length(mice)
                subplot(ceil(length(mice)/ceil(sqrt(length(mice)))),ceil(sqrt(length(mice))),imouse)
                [sessions,session_tmst] = fetchn(beh.Session & 'exp_type="CenterPort"' & sprintf('animal_id = %d',mice(imouse)),'session_id','session_tmst');
                days = datenum(session_tmst);
                [un_days,un_idx] = unique(round(days));
              
                trials = nan(length(un_days),1);
              
                for isession = 1:length(un_days)
                    trials(isession) = count(beh.Trial  & ...
                        sprintf('session_id > %d AND session_id < %d',sessions(un_idx(isession))-1,sessions(un_idx(isession))+1) ...
                        & sprintf('animal_id = %d',mice(imouse))) ;
                end
                plot(trials)
                hold on
                plot([1 isession],[0.5 0.5],'-.','color',[0.6 0.6 0.6])
                set(gca,'xtick',1:4:isession,'xticklabel',datestr(un_days(1:4:isession)),'XTickLabelRotation',45)
                title(sprintf('%d',mice(imouse)))
                xlim([1 isession])
                ylim([0 1000])
                set(gca,'box','off')
                set(gcf,'name','Trial count per day')
                if imouse==1
                    ylabel('Trial count / Day')
                end
            end
        end
    end
end
