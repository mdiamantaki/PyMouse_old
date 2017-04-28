%{
beh.SetupInfo (lookup) # 
setup           : varchar(256)           # Setup name
---
ip                          : varchar(16)                   # setup IP address
state="ready"               : enum('ready','running','stopped','sleeping') # 
animal_id=null              : int                           # animal id
task_idx=null               : int                           # task identification number
task="train"                : enum('train','calibrate')     # 
%}


classdef SetupInfo < dj.Relvar
end
