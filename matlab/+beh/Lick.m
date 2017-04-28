%{
beh.Lick (manual) # Lick timestamps
-> beh.Session
time            : int                    # time from session start (ms)
---
probe                       : int                           # probe number
%}


classdef Lick < dj.Relvar
    
    methods
        function plot(obj,varargin)
            
            params.factor = 1;
            params.color = [0 0 1];
            params = getParams(params,varargin);
            
            times = msec2tmst(fetch(beh.Session & obj),fetchn(obj,'time'));
            plot(times,ones(size(times)) * params.factor,'.','color',params.color)
        end
        
        function plotTrial(obj, varargin)
            
            params.average = 1;
            params.sub = 8;
            params.bin = 0.5;
            params.time_lim = [-0.5 5];
            params.prob = 0;
            params.response = 0;
            
            params = getParams(params, varargin);
            
            for key=fetch(beh.Session & obj)'
                figure
                set(gcf,'name',sprintf('Licks Animal:%d Session:%d',key.animal_id,key.session_id))
                colors = [0 0 1; 1 0 0];
                conds = fetch(beh.Condition & key); sub = [];
                for icond = 1:length(conds)
                    if params.sub > 1
                        sub(icond) = subplot(params.sub,length(conds),icond:length(conds):length(conds)*(params.sub-1));  hold on
                    else
                        sub(icond) = subplot(1,length(conds),icond);  hold on
                    end
                    
                    % get data
                    tdur = fetch1(beh.Session & key,'trial_duration')/60;
                    wtimes = fetchn(beh.Trial & key & conds(icond),'start_time')/1000/60;
                    [ltimes, probes] = ...
                        (fetchn(beh.Lick & key & conds(icond),'time','probe'));
                    ltimes = ltimes/1000/60; % convert to minutes
                    
                    % calculate start and stop times
                    start = (wtimes + params.time_lim(1));
                    stop = [wtimes(2:end); wtimes(end)+(wtimes(end)-wtimes(end-1))];
                    [LickIdx,trialIdx] = find(bsxfun(@gt,ltimes,start') & bsxfun(@lt,ltimes,stop'));
                    Ltimes = ltimes(LickIdx)-wtimes(trialIdx);
                    
                    % plot Licks
                    for iprobe = unique(probes(LickIdx))'
                        idx = probes(LickIdx)==iprobe;
                        plot(Ltimes(idx),trialIdx(idx),'.','color',colors(iprobe,:))
                    end
                    
                    % show reward &  punishment
                    if params.response 
                        [rtimes, rprobes] = ...
                            (fetchn(beh.LiquidDelivery & key & conds(icond),'time','probe'));
                        [ptimes, pprobes] = ...
                            (fetchn(beh.AirpuffDelivery & key & conds(icond),'time','probe'));
                        rtimes = rtimes/1000/60; ptimes = ptimes/1000/60; % convert to minutes
                        
                        % calculate indexes
                        [RewIdx,rtrialIdx] = find(bsxfun(@gt,rtimes,start') & bsxfun(@lt,rtimes,stop'));
                        Rtimes = rtimes(RewIdx)-wtimes(rtrialIdx);
                        [PunIdx,ptrialIdx] = find(bsxfun(@gt,ptimes,start') & bsxfun(@lt,ptimes,stop'));
                        Ptimes = ptimes(PunIdx)-wtimes(ptrialIdx);

                        % plot Reward & punishment
                        for iprobe = unique(probes)' 
                            idx = rprobes(RewIdx)==iprobe;
                            plot(Rtimes(idx),rtrialIdx(idx),'o','color',colors(iprobe,:))
                            idx = pprobes(PunIdx)==iprobe;
                            plot(Ptimes(idx),ptrialIdx(idx),'*','color',colors(iprobe,:))
                        end
                    end
                    
                    % adjust plot settings
                    set(gca,'ydir','reverse','box','off')
                    xlim(params.time_lim)
                    ylim([0 length(wtimes)+ 1])
                    plot([0 0],[1 length(wtimes)],'color',[0.5 0.5 0.5],'linewidth',1)
                    plot([tdur tdur],[1 length(wtimes)],'--','color',[0 0 0],'linewidth',1)
                    if icond==1
                        ylabel('Trial #')
                        set(gca,'ytick',get(gca,'ylim'))
                    else
                        set(gca,'ytick',[])
                    end
                    [mov, clip] = fetch1(beh.MovieClipCond & key & conds(icond),'movie_name','clip_number');
                    rprob = fetch1(beh.RewardCond & key & conds(icond),'probe');
                    title(sprintf('Movie: %s  Clip: %d \n Reward Probe:%d',mov, clip, rprob))
                    
                    % average licking plots
                    if params.average
                        set(gca,'xtick',[],'XColor',[1 1 1])
                        s(icond) = subplot(params.sub,length(conds),length(conds)*(params.sub-1) + icond);  hold on
                        
                        P = probes(LickIdx);
                        if ~params.prob
                            [N, ~] = histcounts(Ltimes(P==1),params.time_lim(1):params.bin:params.time_lim(2) + params.bin,...
                                'normalization','probability');
                            [N2, bins] = histcounts(Ltimes(P==2),params.time_lim(1):params.bin:params.time_lim(2) + params.bin,...
                                'normalization','probability');
                        else
                            bins = params.time_lim(1)-params.bin:params.bin:params.time_lim(2) + params.bin;
                            N = zeros(size(wtimes,1),size(bins,2)-1); N2 = N;
                            for itrial = 1:length(wtimes)
                                idx = trialIdx==itrial;
                                for ibin = 2:length(bins)
                                    N(itrial,ibin-1) = any(Ltimes(idx)<bins(ibin) & Ltimes(idx)>=bins(ibin-1) & P(idx)==1);
                                    N2(itrial,ibin-1) = any(Ltimes(idx)<bins(ibin) & Ltimes(idx)>=bins(ibin-1) & P(idx)==2);
                                end
                            end
                            N = mean(N);
                            N2 = mean(N2);
                        end
                        plot(bins(2:end-1)-params.bin/2,N(1:end-1),'b')
                        plot(bins(2:end-1)-params.bin/2,N2(1:end-1),'r')
                        plot(bins(2:end-1)-params.bin/2,N(1:end-1),'.b','markersize',6)
                        plot(bins(2:end-1)-params.bin/2,N2(1:end-1),'.r','markersize',6)
                        xlim(params.time_lim)
                        MX(icond) = max([N N2]);
                        if icond==1
                            xlabel('Time (min)')
                            ylabel('P(lick)')
                            l = legend('Probe #1','Probe #2');
                            set(l,'box','off')
                        else
                            set(gca,'ytick',[])
                        end
                    else
                        if icond==1; xlabel('Time (min)');end
                    end
                end
            end
            if params.average
                linkaxes(s,'xy')
                ylim([0 max(MX)])
            end
            linkaxes(sub,'xy')
        end
    end
end














