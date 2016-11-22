from TimeConverter import*

class TimeLine:
    def __init__(self, parent):
        self.parent = parent
        self.curr_time = 0
        self.time_list = []
        self.tl_point_list = []
        self.event_count = 0

    def set_time_slider(self, point_list):
        """ Sets time_slider range. """
        start = int(point_list[0].time)
        end = int(point_list[-1].time)
        time = end - start
        return start, end, time

    def get_curr_time(self, time, point_list):
        """ Displays time_slider slider setting and send list of point
        times to bisect. """
        time_list = []
        start = point_list[0].time
        self.curr_time = int(time + start)
        for point in point_list:
            point_time = point.time
            point_time -= start
            time_list.append(point_time)
        tc = TimeConverter()
        display = tc.get_time_hrs_mins(self.curr_time)
        #self.bisect(time_list, start)
        return display, time_list, start

    def zero_time_list(self):
        self.time_list = []
        self.tl_point_list = []

    def mark_time(self):
        """ Gets start and finish times and calculates total
        hours worked.
        Allows times to be changed and recalculates total.
        """
        tc = TimeConverter()
        if self.event_count >= 2:
            self.zero_time_list()
            self.event_count = 0
        self.time_list.append(self.curr_time)
        start = self.time_list[0]
        finish = self.time_list[-1]
        hours = finish - start
        start_time = tc.get_time_hrs_mins(start)
        end_time = tc.get_time_hrs_mins(finish)
        hours_done = tc.get_time_hrs_mins(hours)
        # positions
        self.tl_point_list.append(self.time_posn)
        self.event_count += 1
        # return to JT key_press_event
        return start_time, end_time, hours_done, self.tl_point_list, start, finish
