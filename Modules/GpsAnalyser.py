#!/usr/bin/python
import xml.etree.ElementTree as ET
import os.path
from decimal import Decimal
import pytz  # For local time adjustment
import datetime
from TimeConverter import*
from TrackPoint import*


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
        #self.time_posn = (0, 0)

        if os.path.isfile(data_file):
            tree = ET.parse('./Logs/' + sel_date + '.gpx')  # Should there be "with open as ..."?
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

                        a_point = TrackPoint(pointID, time, lat, lon, course)
                        self.point_list.append(a_point)
                        pointID += 1
        # return to JobTracker get_track()
        return self.point_list




