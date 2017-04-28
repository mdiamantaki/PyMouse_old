%{
beh.MouseWeight (manual) # Weight of the animal
animal_id       : int                    # animal id
timestamp       : timestamp              # 
---
weight                      : float                         # in grams
%}


classdef MouseWeight < dj.Relvar
end
