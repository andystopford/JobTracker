class TrackPoint:
    def __init__(self, pointID, time, lat, lon, course):
        self.pointID = pointID
        self.time = time
        self.lat = lat
        self.lon = lon
        self.course = course

    def get_pointID(self):
        return self.pointID

    def get_time(self):
        return self.time

    def get_lat(self):
        return self.lat

    def get_lon(self):
        return self.lon

    def get_course(self):
        return self.course