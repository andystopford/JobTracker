#!/usr/bin/python
import xml.etree.ElementTree as ET
import os.path
from decimal import Decimal
import pytz  # For local time adjustment
import datetime
from TimeConverter import*
from TrackPoint import*
import geopy, geopy.distance
from bisect import bisect_left  # For getting closest numbers in list
from math import *


class GpsAnalyser():
    def __init__(self, parent):
        self.parent = parent
        self.point_list = []
        self.location_list = []

    def get_data(self, sel_date):
        pointID = 0
        jobID = ''
        time = ''
        lat = ''
        lon = ''
        course = ''
        data_file = './Logs/' + sel_date + '.gpx'
        if os.path.isfile(data_file):
            tree = ET.parse('./Logs/' + sel_date + '.gpx')
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
                    wet = pytz.timezone('WET')
                    date_time = datetime.datetime(year, month, day, hour, mins, secs)
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
                        for item in trackPnt.iter():  # i.e. iterate through children of trackPnts
                            if item.tag == name_space + 'time':
                                time = item.text
                                time = time[11:16]  # We only want hours and minutes.
                                timeConverter = TimeConverter()
                                time_TC = timeConverter.get_time_mins(time)  # convert to mins
                                # Add offset + 60 because of phone weirdness
                                time = time_TC + (int(timezone_offset) * 60) + 60
                            if item.tag == name_space + 'course':
                                course = item.text
                            if item.tag == name_space + 'speed':
                                speed = item.text
                            if item.tag == name_space + 'ele':
                                height = item.text
                        a_point = TrackPoint(pointID, time, lat, lon, course, speed, height)
                        self.point_list.append(a_point)
                        pointID += 1
        # return to JobTracker get_track()
        return self.point_list

    def bisect(self, time_list, start):
        """ Compares the parent.time_slider slider setting with
        point_list to find the nearest point times before
        and after """
        sel_time = self.parent.ui.time_slider.value()
        pos = bisect_left(time_list, sel_time)
        before = time_list[pos - 1]
        after = time_list[pos]
        # return to JobTracker get_curr_time()
        return before, after, start

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
        rlat1 = radians(latitude_1)
        rlat2 = radians(latitude_2)
        rlon1 = radians(longitude_1)
        rlon2 = radians(longitude_2)
        drlon = rlon2 - rlon1
        b = atan2(sin(drlon) * cos(rlat2), cos(rlat1) * sin(rlat2) -
                  sin(rlat1) * cos(rlat2) * cos(drlon))
        return (degrees(b) + 360) % 360

