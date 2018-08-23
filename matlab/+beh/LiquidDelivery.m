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
        
        function plotDays(obj, varargin)
            
            mice = unique(fetchn(obj & 'animal_id>0','animal_id'));
            for imouse = 1:length(mice)
                figure
                daytimeFunc = @(sesstime, times) datenum(sesstime,'YYYY-mm-dd HH:MM:SS') + times/1000/3600/24;
                k.animal_id = mice(imouse);
                [times, sess_times, rew] = fetchn(obj * beh.Session & k,...
                    'time','session_tmst','reward_amount');
                dtimes = daytimeFunc(sess_times,times);
                [days, ~, IC]= unique(floor(dtimes),'rows');
                TotalReward = nan(length(days),1);
                for iday = 1:length(days)
                    TotalReward(iday) = sum(rew(IC==iday));
                end
                plot(TotalReward/1000)
                set(gca,'xtick',1:iday,'xticklabel',datestr(days),'XTickLabelRotation',45)
                hold on
                plot([1 iday],[1 1],'-.r')
                ylim([0 3])
                ylabel('Delivered liquid (ml)')
                title(sprintf('Animal ID %d',mice(imouse)))
            end
        end
     end
    
end

