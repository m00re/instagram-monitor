# Instagram Activity Monitor
 
This is a small Flask-based Python application that periodically parses a given Instagram profile, extracts the
publically available information and stores it into a local MySQL database. The data is stored as a time series and
enables the evolution of the follower count of the profile itself, as well as the evolution of like/comment counts of
individual posts. 