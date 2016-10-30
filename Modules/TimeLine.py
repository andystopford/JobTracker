from TimeConverter import*
import geopy, geopy.distance
from bisect import bisect_left  # For getting closest numbers in list
from math import *
from TimeConverter import*

class TimeLine:
    def __init__(self, parent):
        self.parent = parent
        self.curr_time = 0
        self.time_list = []
        self.point_list = []
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
        self.bisect(time_list, start)
        return display
    
    def bisect(self, time_list, start):
        """ Compares the parent.time_slider slider setting with
        point_list to find the nearest point times before
        and after """
        sel_time = self.parent.ui.time_slider.value()
        pos = bisect_left(time_list, sel_time)
        """
        if pos == 0:
            return time_list[0] # where's it returning to?
        if pos == len(time_list):
            return time_list[-1]
        """
        before = time_list[pos - 1]
        after = time_list[pos]
        self.get_coords(before, after, start)
    
    def get_coords(self, before, after, start):
        """ Gets coordinates for before/after pair.
        TODO use this to get points for track segment"""
        for point in self.parent.point_list:
            if point.time - start == before:
                bef_lat = point.lat
                bef_lon = point.lon
                bef_time = point.time
            if point.time - start == after:
                aft_lat = point.lat
                aft_lon = point.lon
                aft_time = point.time
        sel_time = self.parent.ui.time_slider.value()
        leg_len = after - before
        leg_time = sel_time - before
        leg_ratio = leg_time / leg_len
        self.find_posn(bef_lat, bef_lon, aft_lat, aft_lon, leg_ratio)
    
    def find_posn(self, bef_lat, bef_lon, aft_lat, aft_lon, leg_ratio):
        """ Interpolate before and after to get position at current time"""
        distance = geopy.distance.VincentyDistance((bef_lat, bef_lon),
                                                   (aft_lat, aft_lon)).miles
        distance *= leg_ratio
        bearing = self.bearing(bef_lat, bef_lon, aft_lat, aft_lon)
        d = geopy.distance.VincentyDistance(miles=distance)
        dest = d.destination(point=(bef_lat, bef_lon), bearing=bearing)
        self.time_posn = (dest.latitude, dest.longitude)
        self.draw_tracker(dest.latitude, dest.longitude, bearing)
    
    def draw_tracker(self, lat, lon, bearing):
        self.parent.ui.mapView.draw_tracker(lat, lon, bearing)
    
    def bearing(self, latitude_1, longitude_1, latitude_2, longitude_2):
        """Calculation of direction between two geographical points"""
        rlat1 = radians(latitude_1)
        rlat2 = radians(latitude_2)
        rlon1 = radians(longitude_1)
        rlon2 = radians(longitude_2)
        drlon = rlon2 - rlon1
    
        b = atan2(sin(drlon) * cos(rlat2), cos(rlat1) * sin(rlat2) -
                  sin(rlat1) * cos(rlat2) * cos(drlon))
        return (degrees(b) + 360) % 360

    def zero_time_list(self):
        self.time_list = []
        self.point_list = []

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
        self.point_list.append(self.time_posn)
        self.event_count += 1
        # return to JT key_press_event
        return start_time, end_time, hours_done, self.point_list
