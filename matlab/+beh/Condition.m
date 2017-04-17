%{
beh.Condition (manual) # unique stimulus conditions
-> beh.Session
cond_idx        : smallint               # unique condition index
---
%}


classdef Condition < dj.Relvar
end