%{
beh.ExperimentType (lookup) # Experiment type
exp_type        : char(128)              # experiment schema
---
description                 : varchar(2048)                 # some description of the experiment
%}


classdef ExperimentType < dj.Relvar
end