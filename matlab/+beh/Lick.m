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
        
        function plotTrial(obj,key, varargin)
            
            params.average = 1;
            params.sub = 8;
            params.bin = 0.5;
            params.time_lim = [-0.5 5];
            params.prob = 0;

            figure
            set(gcf,'name',sprintf('Licks Animal:%d Session:%d',key.animal_id,key.session_id))
            colors = [0 0 1; 1 0 0];
            conds = fetch(beh.Condition & key);
            for icond = 1:length(conds)
                if params.sub > 1
                    subplot(params.sub,length(conds),icond:length(conds):length(conds)*(params.sub-1));  hold on
                else
                    subplot(1,length(conds),icond);  hold on
                end
                
                tdur = fetch1(beh.Session & key,'trial_duration')/60;
                wtimes = fetchn(beh.Trial & key & conds(icond),'start_time')/1000/60;
                [ltimes, probes] = ...
                    (fetchn(beh.Lick & key & conds(icond),'time','probe'));
                ltimes = ltimes/1000/60;
                L = [];P = [];
                for iTrial = 1 : length(wtimes)
                    if iTrial ~= length(wtimes)
                        idx = ltimes > (wtimes(iTrial) + params.time_lim(1)) & ltimes < wtimes(iTrial1);
                    else
                        idx = (ltimes > wtimes(iTrial));
                    end
                    licks = ltimes(idx);
                    cols = colors(probes(idx),:);
                    L{iTrial} = licks - wtimes(iTrial);
                    P{iTrial} = probes(idx);
                    for ilick = 1:length(licks)
                        plot(licks(ilick)-wtimes(iTrial),iTrial,'.','color',cols(ilick,:))
                    end
                end
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
                
                if params.average
                    set(gca,'xtick',[],'XColor',[1 1 1])
                    s(icond) = subplot(params.sub,length(conds),length(conds)*(params.sub-1) + icond);  hold on

                    if ~params.prob
                        LL = cell2mat(L');
                        PP = cell2mat(P');
                        [N, bins] = histcounts(LL(PP==1),params.time_lim(1):params.bin:params.time_lim(2) + params.bin,...
                            'normalization','probability');
                        [N2, bins] = histcounts(LL(PP==2),params.time_lim(1):params.bin:params.time_lim(2) + params.bin,...
                            'normalization','probability');              
                    else
                        bins = params.time_lim(1)-params.bin:params.bin:params.time_lim(2) + params.bin;
                        N = nan(length(L),length(bins)-1);
                        N2 = nan(length(L),length(bins)-1);
                        for ibin = 2:length(bins)
                            N(:,ibin-1) = cellfun(@(y,yp) any(y<bins(ibin) & y>=bins(ibin-1) & yp==1),L,P);
                            N2(:,ibin-1) = cellfun(@(y,yp) any(y<bins(ibin) & y>=bins(ibin-1) & yp==2),L,P);
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
            if params.average
               linkaxes(s,'xy')
               ylim([0 max(MX)])
            end
        end
    end
end














