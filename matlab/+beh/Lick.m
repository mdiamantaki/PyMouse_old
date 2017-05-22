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
        
        function plotTrial(obj, restrict, varargin)
            
            params.average = 1;
            params.sub = 8;
            params.bin = 0.5;
            params.time_lim = [-0.5 5];
            params.prob = 0;
            params.response = 0;
            
            
            params = getParams(params, varargin);
            
            if isempty(restrict) || ~isstruct(restrict)
                mice = fetchn(beh.SetupInfo & 'animal_id>0','animal_id');
                keys = [];
                for imouse=1:length(mice)
                    keys(imouse).animal_id = mice(imouse);
                    k.animal_id = mice(imouse);
                    if strcmp(restrict,'full')
                        sessions = fetch(beh.Session & k & (beh.MovieClipCond & 'movie_name="obj1v4"') & ...
                            (beh.MovieClipCond & 'movie_name="obj2v4"'),'ORDER BY session_id DESC');
                    else
                        sessions = fetch(beh.Session & k ,'ORDER BY session_id DESC');
                    end
                    keys(imouse).session_id = sessions(1).session_id;
                end
                keys = keys';
                assert(~isempty(keys),'no keys specified!')
            else
                keys = fetch(beh.Session & restrict);
            end
            
            for key=keys'
                
                figure
                set(gcf,'name',sprintf('Licks Animal:%d Session:%d',key.animal_id,key.session_id))
                colors = [0 0 1; 1 0 0];
                conds = fetch(beh.Condition & key); sub = nan(length(conds),1);s = sub;
                for icond = 1:length(conds)
                    if params.sub > 1
                        sub(icond) = subplot(params.sub,length(conds),icond:length(conds):length(conds)*(params.sub-1)); hold on
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
                    rprob = fetch1(beh.RewardCond & key & conds(icond),'probe');
                    if count(beh.MovieClipCond & conds(1))>0
                        [mov, clip] = fetch1(beh.MovieClipCond & key & conds(icond),'movie_name','clip_number');
                        title(sprintf('Movie: %s  Clip: %d \n Reward Probe:%d',mov, clip, rprob))
                    elseif count(beh.GratingCond & conds(1))
                        direction = fetch1( beh.GratingCond & key & conds(icond),'direction');
                        title(sprintf('Direction: %d \n Reward Probe:%d',direction, rprob))
                    end
                    
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
                            label = 'Lick rate';
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
                            label = 'P(lick)';
                        end
                        plot(bins(2:end-1)-params.bin/2,N(1:end-1),'b')
                        plot(bins(2:end-1)-params.bin/2,N2(1:end-1),'r')
                        plot(bins(2:end-1)-params.bin/2,N(1:end-1),'.b','markersize',6)
                        plot(bins(2:end-1)-params.bin/2,N2(1:end-1),'.r','markersize',6)
                        xlim(params.time_lim)
                        MX(icond) = max([N N2]);
                        if icond==1
                            xlabel('Time (min)')
                            ylabel(label)
                            l = legend('Probe #1','Probe #2');
                            set(l,'box','off')
                        else
                            set(gca,'ytick',[])
                        end
                    else
                        if icond==1; xlabel('Time (min)');end
                    end
                end
                linkaxes(sub,'xy')
                if params.average
                    linkaxes(s,'xy')
                    ylim([0 max([MX eps])])
                end
            end
            
        end
        
        function plotDelay(obj, varargin)
            
            params.type = 'all';
            
            params = getParams(params,varargin);
            
            % function to convert times to days
            daytimeFunc = @(sesstime, times) datenum(sesstime,'YYYY-mm-dd HH:MM:SS') - 18/24 + times/1000/3600/24;
            
            mice = fetch(beh.SetupInfo & 'animal_id>0','animal_id');
            colors = cbrewer('qual','Dark2',length(mice));
            figure; hold on
            for imouse = 1:length(mice)
                key = fetch(beh.Session & mice(imouse) & beh.MovieClipCond,'ORDER BY session_id');
                [start_times, end_times, session_times] = fetchn(beh.Trial * beh.Session & key, 'start_time','end_time','session_tmst');
                start_times = daytimeFunc(session_times, start_times);
                end_times = daytimeFunc(session_times, end_times);
                [days, IA, IC]= unique(floor(start_times),'rows');
                
                [rew_times, rProbe, session_timesR] = fetchn(beh.LiquidDelivery * beh.Session & key,'time','probe','session_tmst');
                resp_times = daytimeFunc(session_timesR, rew_times);
                [pun_times, pProbe, session_times] = fetchn(beh.AirpuffDelivery * beh.Session & key,'time','probe','session_tmst');
                resp_times(end+1:end+length(pun_times)) = daytimeFunc(session_times, pun_times);
                probes = [rProbe; pProbe];
                delays = nan(length(days),2);
                for iday = unique(IC)'
                    
                    switch params.type
                        case 'all' % All responses
                            stimes = start_times(IC==iday)';
                            stimes = repmat(stimes,[size(resp_times,1),1]);
                            etimes = end_times(IC==iday)';
                            etimes = repmat(etimes,[size(resp_times,1),1]);
                            probesM = repmat(probes,[1, size(stimes,2)]);
                            rtimesM = repmat(resp_times,[1 size(stimes,2)]);
                            
                            idx = rtimesM>=stimes & rtimesM <= etimes ;
                            val = (rtimesM(idx) - stimes(idx))*24*3600;
                            delays(iday,1) = mean(val);
                            delays(iday,2) = std(val)/sqrt(length(val));
                            
                        case 'probe' % Probe 1 vs probe 2
                            stimes = start_times(IC==iday)';
                            stimes = repmat(stimes,[size(resp_times,1),1]);
                            etimes = end_times(IC==iday)';
                            etimes = repmat(etimes,[size(resp_times,1),1]);
                            probesM = repmat(probes,[1, size(stimes,2)]);
                            rtimesM = repmat(resp_times,[1 size(stimes,2)]);
                            
                            idx = rtimesM>=stimes & rtimesM <= etimes & probesM==1;
                            delays(iday,1) = mean(rtimesM(idx) - stimes(idx))*24*3600;
                            
                            idx = rtimesM>=stimes & rtimesM <= etimes & probesM==2;
                            delays(iday,2) = mean(rtimesM(idx) - stimes(idx))*24*3600;
                            
                        case 'value' % Correct vs wrong
                            resp_times = daytimeFunc(session_timesR, rew_times);
                            stimes = start_times(IC==iday)';
                            stimes = repmat(stimes,[size(resp_times,1),1]);
                            etimes = end_times(IC==iday)';
                            etimes = repmat(etimes,[size(resp_times,1),1]);
                            rtimesM = repmat(resp_times,[1 size(stimes,2)]);
                            idx = rtimesM>=stimes & rtimesM <= etimes;
                            delays(iday,1) = mean(rtimesM(idx) - stimes(idx))*24*3600;
                            
                            resp_times = daytimeFunc(session_times, pun_times);
                            stimes = start_times(IC==iday)';
                            stimes = repmat(stimes,[size(resp_times,1),1]);
                            etimes = end_times(IC==iday)';
                            etimes = repmat(etimes,[size(resp_times,1),1]);
                            rtimesM = repmat(resp_times,[1 size(stimes,2)]);
                            idx = rtimesM>=stimes & rtimesM <= etimes;
                            delays(iday,2) = mean(rtimesM(idx) - stimes(idx))*24*3600;
                    end
                end
                % plot
                switch params.type
                    case 'all'
                        errorPlot(1:size(delays,1),[],'manual',delays','errorColor',colors(imouse,:))
                    otherwise
                        plot(delays(:,1),'color',colors(imouse,:))
                        plot(delays(:,2),'color',colors(imouse,:))
                end
            end
            grid on
            l = legend(arrayfun(@num2str,[mice.animal_id],'uni',0));
            set(l,'box','off')
            ylabel('Lick delay (s)')
            xlabel('Time (days)')
        end
    end
end














