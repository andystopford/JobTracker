class TrackPoint:
    def __init__(self, pointID, time, lat, lon, course, speed, height):
        self.pointID = pointID
        self.time = time
        self.lat = lat
        self.lon = lon
        self.course = course
        self.speed = speed
        self.height = height

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

    def get_speed(self):
        return self.speed

    def get_height(self):
        return self.height