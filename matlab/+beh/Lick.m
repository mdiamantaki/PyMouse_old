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
            params.bin = 2.5;
            params.time_lim = [-2.5 5];
            params.prob = 1;
            params.response = 0;
            params.fontsize = 12;
            
            
            params = getParams(params, varargin);
            
            if (nargin<2 || isempty(restrict)) || (~isstruct(restrict) && ~isobject(restrict))
                [mice,state] = fetchn(beh.SetupInfo & beh.Condition & beh.Trial & 'animal_id>0','animal_id','state');
                keys = [];
                for imouse=1:length(mice)
                    keys(imouse).animal_id = mice(imouse);
                    k.animal_id = mice(imouse);
                    sessions = fetch(beh.Session & beh.Condition & beh.Trial & k ,'ORDER BY session_id DESC');
                    if (nargin>1 && strcmp(restrict,'now')) || ~strcmp(state{imouse},'running')
                        sess_idx = 1;
                    else
                        sess_idx = 2;
                    end
                   
                    keys(imouse).session_id = sessions(sess_idx).session_id;
                end
                keys = keys';
                assert(~isempty(keys),'no keys specified!')
            else
                if isstruct(restrict)
                    keys = fetch(beh.Session & restrict);
                else
                    keys = fetch(restrict);
                end
            end
            
            for key=keys'
                
                colors = [0 0 1; 1 0 0];
                conds = fetch(beh.Condition & key); sub = nan(length(conds),1);s = sub;
                date = datestr(fetch1(beh.Session & key,'session_tmst'),'YYYY-mm-dd');
                if ~isempty(conds) && exists(beh.Trial & key) && count(beh.Trial & key)>0
                    figure
                    set(gcf,'name',sprintf('Licks Animal:%d Day:%s Session:%d',key.animal_id,date,key.session_id))
                else
                    continueclo
                end
                for icond = 1:length(conds)
                    if params.sub > 1
                        sub(icond) = subplot(params.sub,length(conds),icond:length(conds):length(conds)*(params.sub-1)); hold on
                    else
                        sub(icond) = subplot(1,length(conds),icond);  hold on
                    end
                    
                    % get data
                    tdur = fetch1(beh.Session & key,'trial_duration');
                    [wtimes, etimes] = fetchn(beh.Trial & key & conds(icond),'start_time','end_time');
                    wtimes = wtimes/1000;
                    etimes = etimes/1000;
                    if isempty(wtimes);fprintf('No trials for animal %d \n',key.animal_id);continue;end
                    wtimes(end+1) = wtimes(end)+1;wtimes = wtimes(:); % FIX THIS
                    [ltimes, probes] = ...
                        (fetchn(beh.Lick & key & conds(icond),'time','probe'));
                    ltimes = ltimes/1000; % convert to minutes
                    
                    % calculate start and stop times
                    start = (wtimes + params.time_lim(1));
                    stop = [wtimes(2:end); wtimes(end)+(wtimes(end)-wtimes(end-1))];
                    [LickIdx,trialIdx] = find(bsxfun(@gt,ltimes,start') & bsxfun(@lt,ltimes,stop'));
                    Ltimes = ltimes(LickIdx)-wtimes(trialIdx);
                    
                    % show reward &  punishment
                    if params.response       
                        [EndIdx,etrialIdx] = find(bsxfun(@gt,etimes,start') & bsxfun(@lt,etimes,stop'));
                          Etimes = etimes(EndIdx)-wtimes(etrialIdx);
                        plot(Etimes,etrialIdx,'x','color',[0.1 0.1 0.1]);
                    
                        [rtimes, rprobes] = ...
                            (fetchn(beh.LiquidDelivery & key & conds(icond),'time','probe'));
                        [ptimes, pprobes] = ...
                            (fetchn(beh.AirpuffDelivery & key & conds(icond),'time','probe'));
                        rtimes = rtimes/1000; ptimes = ptimes/1000; % convert to minutes
                        
                        % calculate indexes
                        [RewIdx,rtrialIdx] = find(bsxfun(@gt,rtimes,start') & bsxfun(@lt,rtimes,stop'));
                        Rtimes = rtimes(RewIdx)-wtimes(rtrialIdx);
                        [PunIdx,ptrialIdx] = find(bsxfun(@gt,ptimes,start') & bsxfun(@lt,ptimes,stop'));
                        Ptimes = ptimes(PunIdx)-wtimes(ptrialIdx);
                        
                        % plot Reward & punishment
                        for iprobe = unique(probes)'
                            idx = rprobes(RewIdx)==iprobe;
                            plot(Rtimes(idx),rtrialIdx(idx),'o','color',[0 1 0])
                            idx = pprobes(PunIdx)==iprobe;
                            plot(Ptimes(idx),ptrialIdx(idx),'*','color',colors(iprobe,:))
                        end
                    end
                    
                    % plot Licks
                    tr = [];
                    for iprobe = unique(probes(LickIdx))'
                        idx = probes(LickIdx)==iprobe;
                        tr{iprobe} = plot(Ltimes(idx),trialIdx(idx),'.','color',colors(iprobe,:));
                    end
                    
                    % adjust plot settings
                    set(gca,'ydir','reverse','box','off')
                    xlim(params.time_lim)
                    ylim([0 length(wtimes)+ 1])
                    t = plot([0 0],[1 length(wtimes)],'color',[0.5 0.5 0.5],'linewidth',1);
                    plot([tdur tdur],[1 length(wtimes)],'--','color',[0 0 0],'linewidth',1)
                    if icond==1
                        ylabel('Trial #','fontsize',params.fontsize)
                        set(gca,'ytick',get(gca,'ylim'),'fontsize',params.fontsize)
                    else
                        set(gca,'ytick',[])
                    end
                    
                    if icond == length(conds)
                         tr{end+1} = t;
                        legnd ={'Probe #1','Probe #2','Trial start'};
                        idx = ~cellfun(@isempty,tr);
                        tr = tr(idx);
                        l = legend([tr{:}],legnd(idx));
                        set(l,'box','off','fontsize',params.fontsize,'location','southeast')
                    end
                    
                    colors = [0 0 1;1 0 0];
                    rprob = fetch1(beh.RewardCond & key & conds(icond),'probe');
                    if count(beh.MovieClipCond & conds(1))>0
                        [mov, clip] = fetch1(beh.MovieClipCond & key & conds(icond),'movie_name','clip_number');
                        title(sprintf('%s %d',mov, clip),'Color', colors(rprob,:),...
                            'rotation',45,'HorizontalAlignment','left','VerticalAlignment','middle')
                    elseif count(beh.GratingCond & conds(1))
                        direction = fetch1( beh.GratingCond & key & conds(icond),'direction');
                        title(sprintf('Direction: %d \n Reward Probe:%d',direction, rprob))
                    elseif count(beh.OdorCond & conds(1))>0
                        odor = fetch1(beh.OdorCond & key & conds(icond),'odor_name');
                        title(sprintf('%s',odor),'Color', colors(rprob,:),...
                            'rotation',45,'HorizontalAlignment','left','VerticalAlignment','middle')
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
                                    lick_det = find(Ltimes(idx)<bins(ibin) & Ltimes(idx)>=bins(ibin-1),1,'first');
                                    probe=P(idx);
                                    if probe(lick_det)==1
                                        N(itrial,ibin-1) =1;
                                        N2(itrial,ibin-1)= 0;
                                    elseif probe(lick_det)==2
                                        N(itrial,ibin-1)=0;
                                        N2(itrial,ibin-1) =1;
                                    else
                                        N(itrial,ibin-1) =0;
                                        N2(itrial,ibin-1) =0;
                                    end
                                    %                                     N(itrial,ibin-1) = any(Ltimes(idx)<bins(ibin) & Ltimes(idx)>=bins(ibin-1) & P(idx)==1);
                                    %                                     N2(itrial,ibin-1) = any(Ltimes(idx)<bins(ibin) & Ltimes(idx)>=bins(ibin-1) & P(idx)==2);
                                end
                            end
                            N = mean(N);
                            N2 = mean(N2);
                            label = 'P(lick)';
                        end
                        plot(bins(2:end-1)-params.bin/2,N(1:end-1),'-.b')
                        plot(bins(2:end-1)-params.bin/2,N2(1:end-1),'-.r')
                        plot(bins(2:end-1)-params.bin/2,N(1:end-1),'.b','markersize',10)
                        plot(bins(2:end-1)-params.bin/2,N2(1:end-1),'.r','markersize',10)
                        xlim(params.time_lim)
                        MX(icond) = max([N N2]);
                        set(gca,'fontsize',params.fontsize)
                        if icond==1
                            xlabel('Time (sec)','fontsize',params.fontsize)
                            ylabel(label,'fontsize',params.fontsize)
                        else
                            set(gca,'ytick',[])
                        end
                        
                    else
                        if icond==1; xlabel('Time (sec)','fontsize',params.fontsize);end
                    end
                end
                linkaxes(sub,'xy')
                if params.average
                    linkaxes(s,'xy')
                    ylim([0 max([MX eps])])
                    linkaxes([sub;s],'x')
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














