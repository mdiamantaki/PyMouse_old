%{
beh.SetupControl (lookup) # 
setup           : varchar(256)           # Setup name
---
ip                          : varchar(16)                   # setup IP address
state="ready"               : enum('initializing','ready','running','stopped','sleeping') # 
state_control=""            : enum('startSession','startScan','stopScan','stopSession','pause','Initialize','')
animal_id=null              : int                           # animal id
session                     : smallint                      # session index for the mouse
scan_idx                    : smallint                      # number of scan file
stimulus=""                 : varchar(1024)                 # stimulus name
last_ping                   : timestamp                     # last timestamp from python
%}


classdef SetupControl < dj.Relvar
end
