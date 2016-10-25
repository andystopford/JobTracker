import sys
import os.path
import shutil
import datetime
import xml.etree.ElementTree as ET
sys.path.append("./Modules")
from PyQt4 import QtCore, QtGui
from Year import *

class DataIO:
    def __init__(self, parent):
        self.path = './Logs'
        self.parent = parent

    def get_gpx(self):
        """Copies .gpx files from Dropbox to ./Logs directory"""
        source_path = '/home/andy/Dropbox/Apps/GPSLogger for Android/'
        source = os.listdir(source_path)
        for gpx_file in source:
            if gpx_file.endswith('gpx'):
                if not os.path.isfile('./Logs/' + gpx_file):
                    shutil.copy2(source_path + gpx_file, './Logs')

    def get_logs(self, curr_year):
        """ Get log files for curr_year (from filename, e.g. 20150829.gpx)"""
        log_list = []
        for log_file in os.listdir('Logs'):
            if not log_file.startswith('.'):  # filter unix hidden files
                year = int(log_file[0:4])
                if year == curr_year:
                    day = int(log_file[6:8])
                    month = int(log_file[4:6])
                    log_list.append([day, month])
                    self.parent.key_list.append(year)
        return log_list

    def open(self):
        with open(self.path, "r") as fo:
            tree = ET.ElementTree(file=self.path)
            root = tree.getroot()
            for date in root:
                comms = date[0]
                acts = date[1]
                infrs = date[2]
                self.add_day(date.text, comms.text, acts.text, infrs.text)

    def add_day(self, date, comments, activities, infringements):
        if date is not None:
            date = QtCore.QDate.fromString(date)
            day = date.day()
            month = date.month()
            year = date.year()
            year_instance = Year(self, year)
            col = year_instance.get_column(month, day)
            row = month - 1
            current_model = self.parent.model_dict[year]
            item = current_model.item(row, col)
            comment = QtGui.QStandardItem()
            activity = QtGui.QStandardItem()
            infringed = QtGui.QStandardItem()
            item.setChild(0, 2, comment)
            item.setChild(0, 3, activity)
            item.setChild(0, 4, infringed)
            comment.setData(comments)
            activity.setData(activities)
            infringed.setData(infringements)
            if infringed.data() is None:
                item.setBackground(QtGui.QColor(109, 255, 174))
            if infringed.data() == "hgv":
                item.setBackground(QtGui.QColor(255, 150, 150))
            if infringed.data() == "wtd":
                item.setBackground(QtGui.QColor(255, 205, 117))
            if infringed.data() == "both":
                pixmap = QtGui.QPixmap('./icons/dual_infr.svg')
                brush = QtGui.QBrush(pixmap)
                item.setBackground(brush)
            self.parent.infringements = ""

    def save(self, model_dict):
        root = ET.Element('Root')
        tree = ET.ElementTree(root)
        for key in model_dict:
            model = model_dict[key]
            # Seems like year needs to be switched to add other years to model_dict
            data = []
            for row in range(model.rowCount()):
                data.append([])
                for column in range(model.columnCount()):
                    item = model.item(row, column)
                    if item.child(0, 3) is not None:
                        date = item.child(0, 1)  # Qdate
                        comments = item.child(0, 2)  # Comments
                        activities = item.child(0, 3)  # Activities
                        infringements = item.child(0, 4)   # Infringements
                        date = date.data()
                        date = date.toString()
                        comments = comments.data()
                        activities = activities.data()
                        infringements = infringements.data()
                        # Set ET sub-elements
                        dte = ET.SubElement(root, "Date")
                        comms = ET.SubElement(dte, 'Comments')
                        acts = ET.SubElement(dte, 'Activities')
                        infrs = ET.SubElement(dte, 'Infringements')
                        dte.text = date
                        comms.text = comments
                        acts.text = activities
                        infrs.text = infringements

        with open(self.path, "wb") as fo:   # Must be 'wb', not 'w' in Python 3
            tree.write(fo)

        # TODO error message if no driver selected



