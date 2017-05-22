%{
beh.MouseWeight (manual) # Weight of the animal
animal_id       : int                    # animal id
timestamp       : timestamp              #
---
weight                      : float                         # in grams
%}


classdef MouseWeight < dj.Relvar
    methods
        function plot(obj)
            
            mice = unique(fetchn(obj & 'animal_id>0','animal_id'));
            k = [];
            for imouse = 1:length(mice)
                figure
                k.animal_id = mice(imouse);
                [timestamps, weights] = fetchn(obj & k,...
                    'timestamp','weight');
                plot(weights)
                set(gca,'xtick',1:length(weights),...
                    'xticklabel',cellfun(@(x) x(1:10),timestamps,'uni',0),'XTickLabelRotation',45)
                hold on
                plot([1 length(weights)],[1 1]*weights(1)*0.7,'-.r')
                plot([1 length(weights)],[1 1]*weights(1)*0.8,'-.','color',[0.9 0.5 0])
                plot([1 length(weights)],[1 1]*weights(1)*0.9,'-.','color',[0.5 0.5 0.5])
                text(length(weights),weights(1)*0.7,'30%','color',[1 0 0])
                text(length(weights),weights(1)*0.8,'20%','color',[0.9 0.5 0])
                text(length(weights),weights(1)*0.9,'10%','color',[0.5 0.5 0.5])
                ylabel('Mouse weight (gr)')
                title(sprintf('Animal ID %d',mice(imouse)))
            end
        end
    end
end
