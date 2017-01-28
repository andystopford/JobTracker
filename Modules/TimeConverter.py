class TimeConverter:
    def __init__(self):
        return

    def get_time_mins(self, time):
        hour = int(time[0:2])
        mins = int(time[3:5])
        hour *= 60
        mins += hour
        return mins

    def get_time_hrs_mins(self, time):
        hours = int(time / 60)
        mins = int(time % 60)
        hours = str(hours)
        mins = str(mins)
        hours = hours.zfill(2)  # Add leading zero to single digits
        mins = mins.zfill(2)
        formatted = hours + ':' + mins
        return formatted

    def get_time_hrs_mins_secs(self, time):
        hours = int(time / 3600)
        mins = int(time / 60)
        secs = int(time % 60)
        hours = str(hours)
        mins = str(mins)
        secs = str(secs)
        hours = hours.zfill(2)  # Add leading zero to single digits
        mins = mins.zfill(2)
        secs = secs.zfill(2)
        return hours, mins, secs

    def calc_duration(self, start, end):
        return end - start

    def fix_lazy(self, time):
        """Re-formats times to 00:00 style e.g. 1.5 = 01:05"""
        punc = time.find('.')
        if punc != -1:
            time = time.split('.')
            hrs = time[0].zfill(2)
            mins = time[1].zfill(2)
            time = hrs + ':' + mins
            print(time)
            return time
        else:
            if len(time) == 1:
                time = time.zfill(2)
            if len(time) == 2:
                time = time + ":00"
            return  time

