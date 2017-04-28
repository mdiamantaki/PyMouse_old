%{
beh.LiquidCalibration (manual) # Liquid delivery calibration sessions for each probe
setup           : varchar(256)           # Setup name
probe           : int                    # probe number
date            : date                   # session date (only one per day is allowed)
---
%}


classdef LiquidCalibration < dj.Relvar
end