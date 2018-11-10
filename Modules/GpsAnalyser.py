import csv
import os.path
import xml.etree.ElementTree as ET
from bisect import bisect_left  # For getting closest numbers in list
from bisect import bisect_right
from datetime import datetime
from decimal import Decimal
from math import *

import geopy
import geopy.distance
import pytz
from TimeConverter import TimeConverter as TC
from TrackPoint import TrackPoint


class GpsAnalyser:
    def __init__(self, parent):
        """Get GPS information from selected log file and performs tracking
        operations on it. CSV (.log) and legacy .gpx files supported."""
        self.parent = parent
        self.point_list = []
        self.location_list = []

    def get_data(self, date):
        """Read log file and generate list of TrackPoints"""
        point_list = []
        date = date[0:8]
        csv_file = './Logs/' + date + '.log'
        gpx_file = './Logs/' + date + '.gpx'
        if os.path.exists(csv_file):
            point_list = self.get_csv_data(csv_file, date)
        elif os.path.exists(gpx_file):
            point_list = self.get_gpx_data(gpx_file)
        # return to JobTracker get_track()
        return point_list

    def get_csv_data(self, csv_file, date):
        """Generate a point list from  .csv formatted (.log) file,
        correcting for clock-change idiocy"""
        pointID = 0
        point_list = []
        #course = 0
        #speed = 0
        with open(csv_file, 'rt') as log:
            reader = csv.reader(log)
            for row in reader:
                time = row[0]
                # Prepend a 0 before 10:00
                if len(time) == 7:
                    time = '0' + time
                hr = time[0:2]
                mins = time[2:4]
                # insert a colon as expected by TimeConverter
                time = hr + ':' + mins
                # Adjust for local time
                hrs_mins = time[0:5]
                time = TC.get_time_mins(self, hrs_mins)
                offset = self.get_local_time(date)
                if offset != '0':
                    time = time + (int(offset) * 60)
                lat = row[1]
                lat = Decimal(lat)
                lat = round(lat, 4)
                lon = row[2]
                lon = Decimal(lon)
                lon = round(lon, 4)
                #ram = row[3]
                #sats = row[4]
                #ram = row[5]
                #if len(row) >= 7:
                #    course = row[6]
                #if len(row) >= 8:
                #    speed = row[7]
                a_point = TrackPoint(pointID, time, lat, lon, 0, 0, 0)
                point_list.append(a_point)
                pointID += 1
        return point_list

    def get_local_time(self, date):
        """Get the timezone offset - hours to add to UTC"""
        year = int(date[0:4])
        month = int(date[4:6])
        day = int(date[6:8])
        d = [year, month, day]
        wet = pytz.timezone('Europe/London')
        date_time = datetime(year, month, day)
        timezone_offset = wet.utcoffset(date_time)
        timezone_offset = str(timezone_offset)
        timezone_offset = timezone_offset[0]
        return timezone_offset

    def bisect(self, time_list, start):
        """ Compares the parent.time_slider slider setting with
        point_list to find the nearest point times before
        and after """
        sel_time = self.parent.ui.time_slider.value()
        pos = bisect_left(time_list, sel_time)  # index of closest
        before = time_list[pos - 1]
        after = time_list[pos]
        # TODO Get point IDs?
        # return to JobTracker get_curr_time()
        return before, after, start

    def get_trail_points(self, time_list):
        """Get before and after points for selected (slider) time to
        enable coloured follower for time marker.
        """
        trail_range = self.parent.ui.range_slider.getValues()
        bef = abs(int(trail_range[0]))
        aft = int(trail_range[1])
        sel_time = self.parent.ui.time_slider.value()
        now = bisect_right(time_list, sel_time)  # index of closest
        # Select range of points
        before_points = self.parent.point_list[now - bef:now]
        after_points = self.parent.point_list[now - 1:now + aft]
        return before_points, after_points

    def get_coords(self, before, after, start):
        """ Gets coordinates for before/after pair.
        TODO use this to get points for track segment"""
        for point in self.parent.point_list:
            if point.time - start == before:
                bef_lat = point.lat
                bef_lon = point.lon
            if point.time - start == after:
                aft_lat = point.lat
                aft_lon = point.lon
        sel_time = self.parent.ui.time_slider.value()
        leg_len = after - before
        leg_time = sel_time - before
        leg_ratio = leg_time / leg_len
        # return to JobTracker get_curr_time()
        return [bef_lat, bef_lon, aft_lat, aft_lon, leg_ratio]

    def find_posn(self, coords):
        """ Interpolate before and after to get position at current time"""
        bef_lat = coords[0]
        bef_lon = coords[1]
        aft_lat = coords[2]
        aft_lon = coords[3]
        leg_ratio = coords[4]
        distance = geopy.distance.VincentyDistance((bef_lat, bef_lon),
                                                   (aft_lat, aft_lon)).miles
        distance *= leg_ratio
        bearing = self.bearing(bef_lat, bef_lon, aft_lat, aft_lon)
        d = geopy.distance.VincentyDistance(miles=distance)
        dest = d.destination(point=(bef_lat, bef_lon), bearing=bearing)
        # return to JobTracker get_curr_time()
        return [dest.latitude, dest.longitude, bearing, distance]

    def bearing(self, latitude_1, longitude_1, latitude_2, longitude_2):
        """Calculation of direction between two geographical points"""
        rlat1 = radians(float(latitude_1))
        rlat2 = radians(float(latitude_2))
        rlon1 = radians(float(longitude_1))
        rlon2 = radians(float(longitude_2))
        drlon = rlon2 - rlon1
        b = atan2(sin(drlon) * cos(rlat2), cos(rlat1) * sin(rlat2) -
                  sin(rlat1) * cos(rlat2) * cos(drlon))
        return (degrees(b) + 360) % 360

    def get_gpx_data(self, log_file):
        """For legacy data"""
        pointID = 0
        point_list = []
        if os.path.isfile(log_file):
            tree = ET.parse(log_file)
            root = tree.getroot()
            name_space = root.tag[:-3]
            for child in root:
                if child.tag == name_space + 'time':
                    date = child.text
                if child.tag == name_space + 'wpt':
                    for item in child:
                        if item.tag == name_space + 'name':
                            jobID = item.text
                if child.tag == name_space + 'trk':
                    trackSeg = child[0]
                    # Find local time offset:
                    year = int(date[0:4])
                    month = int(date[5:7])
                    day = int(date[8:10])
                    hour = int(date[11:13])
                    mins = int(date[14:16])
                    secs = int(date[17:19])
                    wet = pytz.timezone('Europe/London')
                    date_time = datetime(year, month, day, hour, mins,
                                                  secs)
                    timezone_offset = wet.utcoffset(date_time)
                    timezone_offset = str(timezone_offset)
                    timezone_offset = timezone_offset[0]
                    for trackPnt in trackSeg:
                        if trackPnt.tag == name_space + 'trkpt':
                            lat = trackPnt.attrib['lat']
                            lat = Decimal(lat)
                            lat = round(lat, 4)
                            lon = trackPnt.attrib['lon']
                            lon = Decimal(lon)
                            lon = round(lon, 4)
                        # Adjust for local time
                        for item in trackPnt.iter():
                            if item.tag == name_space + 'time':
                                time = item.text
                                time = time[11:16]
                                time = TC.get_time_mins(self, time)
                                if timezone_offset != '0':
                                    # Add offset +60 because of phone weirdness
                                    time = time + (int(timezone_offset) * 60) \
                                           + 60
                            if item.tag == name_space + 'course':
                                course = item.text
                            if item.tag == name_space + 'speed':
                                speed = item.text
                            if item.tag == name_space + 'ele':
                                height = item.text
                        a_point = TrackPoint(pointID, time, lat, lon, course,
                                             speed, height)
                        point_list.append(a_point)
                        pointID += 1
        # return to JobTracker get_track()
        return point_list
