from PyQt4 import QtCore
from TimeConverter import*


class Timer:
    def __init__(self, parent):
        """Timer to record hours working at the computer"""
        self.parent = parent
        self.qTimer = QtCore.QTimer()
        QtCore.QObject.connect(self.qTimer, QtCore.SIGNAL("timeout()"), self.display_time)
        self.total_time = 0

    def display_time(self):
        now = QtCore.QTime.currentTime()
        elapsed = self.start.secsTo(now)
        disp_time = TimeConverter.get_formatted_hrs_mins_secs(self, elapsed)
        self.parent.ui.time_running.setText(disp_time)

    def timer_start(self):
        self.start = QtCore.QTime.currentTime()
        self.display_time()
        self.qTimer.start(1000)  # Interval at which timer checks time & calls display_time()

    def timer_pause(self):
        stop = QtCore.QTime.currentTime()
        elapsed = self.start.secsTo(stop)
        self.qTimer.stop()
        self.total_time += elapsed
        # divide by sixty to get minutes - comment out for testing
        # minutes = int(self.total_time/60)
        minutes = self.total_time
        disp_time = TimeConverter.get_time_hrs_mins(self, minutes)
        return disp_time

    def timer_clear(self):
        self.total_time = 0

