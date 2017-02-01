import os.path
import shutil
import sys
import xml.etree.ElementTree as ET

sys.path.append("./Modules")
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

    def save(self, model_dict):
        self.parent.ui.hoursTable.update_tracks()
        root = ET.Element('Root')
        tree = ET.ElementTree(root)
        for key in model_dict:
            model = model_dict[key]
            # Seems like year needs to be switched to add other years to model_dict
            #data = []
            for row in range(model.rowCount()):
                #data.append([])
                for column in range(model.columnCount()):
                    item = model.item(row, column)
                    if item.child(0, 0):
                        date = item.child(0, 0).data()
                        date = date.toString('dd.MM.yyyy')
                        tkt_list = item.child(0, 1).data()
                        for tkt in tkt_list:
                            name = tkt.get_name()
                            type = tkt.get_type()
                            notes = tkt.get_notes()
                            track_list = tkt.get_tracks()
                            expenses_list = tkt.get_expenses()

                            # Set ET sub-elements
                            tkt_name = ET.SubElement(root, "Name")
                            tkt_type = ET.SubElement(tkt_name, 'Type')
                            tkt_notes = ET.SubElement(tkt_name, 'Notes')
                            tkt_tracks = ET.SubElement(tkt_name, 'Tracks')
                            tkt_expenses = ET.SubElement(tkt_name, 'Expenses')

                            tkt_name.text = name
                            tkt_type.text = type
                            tkt_notes.text = notes
                            for i, track in enumerate(track_list):
                                trk = ET.SubElement(tkt_tracks, ('Track' + str(i)))
                                trk.set('start', track.get_start())
                                trk.set('end', track.get_end())
                                trk.set('hours', track.get_hours())
                                trk.set('miles', track.get_miles())
                                trk.set('notes', track.get_notes())
                                trk.set('colour', track.get_colour())
                                #trk.set('gps', track.get_gps())


        with open('file.xml', "wb") as fo:   # Must be 'wb', not 'w' in Python 3
            tree.write(fo)

        # TODO error message if no driver selected



