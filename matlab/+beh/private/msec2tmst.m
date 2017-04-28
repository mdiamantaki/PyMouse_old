function tmst = msec2tmst(key, msec_since_session_start)

msec2days = @(x) x/1000/60/60/24;

sess_tmst = fetch1(beh.Session & key,'session_tmst');
sess_tmst = datenum(sess_tmst,'yyyy-mm-dd HH:MM:SS');
tmst = datetime(datevec(msec2days(msec_since_session_start) + sess_tmst));
