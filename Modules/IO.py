import os.path
import shutil
import sys
import xml.etree.ElementTree as ET

from PyQt4 import QtGui

sys.path.append("./Modules")
from Year import *
from Ticket import Track


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
        with open('file.xml', "r") as fo:
            tree = ET.parse(fo)
            root = tree.getroot()
            for date in root:
                year = date.get('date')
                year = int(year[6:10])
                row = int(date.get('row'))
                col = int(date.get('col'))
                model = self.parent.model_dict[year]
                for tkt in date:
                    name = tkt.text
                    cat = tkt[0].text
                    notes = tkt[1].text
                    tracks = tkt[2]
                    ticket = model.add_ticket(row, col, cat)
                    ticket.set_name(name)
                    ticket.set_notes(notes)
                    for trk in tracks:
                        start = trk.get('start')
                        end = trk.get('end')
                        hours = trk.get('hours')
                        miles = trk.get('miles')
                        trk_notes = trk.get('notes')
                        colour = trk.get('colour')
                        colour = QtGui.QColor(colour)
                        colour.setAlpha(127)
                        brush = QtGui.QBrush(colour)
                        track = Track(start, end, hours, miles, trk_notes, brush)
                        ticket.add_track(track)
                    expenses = tkt[3]
                    for exp in expenses:
                        item = exp.get('item')
                        cost = exp.get('cost')
                        expense = [item, cost]
                        ticket.add_expense(expense)
        self.parent.clear_year()

    def save(self, model_dict):
        # Check all entered data is in model:
        self.parent.stateMachine.new_date()
        self.parent.ui.hoursTable.update_tracks()
        # Construct elementtree
        root = ET.Element('Root')
        tree = ET.ElementTree(root)
        for key in model_dict:
            model = model_dict[key]
            # Seems like year needs to be switched to add other years to model_dict
            for row in range(model.rowCount()):
                for col in range(model.columnCount()):
                    item = model.item(row, col)
                    if item.child(0, 0):
                        date = item.child(0, 0).data()
                        date = date.toString('dd.MM.yyyy')
                        tkt_list = item.child(0, 1).data()
                        if tkt_list:
                            tkt_date = ET.SubElement(root, "Date")
                            for tkt in tkt_list:
                                name = tkt.get_name()
                                cat = tkt.get_cat()
                                notes = tkt.get_notes()
                                track_list = tkt.get_tracks()
                                expenses_list = tkt.get_expenses()
                                # Set ET sub-elements
                                tkt_name = ET.SubElement(tkt_date, "Name")
                                tkt_cat = ET.SubElement(tkt_name, 'Cat')
                                tkt_notes = ET.SubElement(tkt_name, 'Notes')
                                tkt_tracks = ET.SubElement(tkt_name, 'Tracks')
                                tkt_expenses = ET.SubElement(tkt_name, 'Expenses')
                                tkt_date.set('row', str(row))
                                tkt_date.set('col', str(col))
                                tkt_date.set('date', date)
                                tkt_name.text = name
                                tkt_cat.text = cat
                                tkt_notes.text = notes
                                for i, track in enumerate(track_list):
                                    trk = ET.SubElement(tkt_tracks, ('Track' + str(i)))
                                    trk.set('start', track.get_start())
                                    trk.set('end', track.get_end())
                                    trk.set('hours', track.get_hours())
                                    trk.set('miles', track.get_miles())
                                    trk.set('notes', track.get_notes())
                                    trk.set('colour', track.get_colour())
                                    # trk.set('gps', track.get_gps())
                                for i, expense in enumerate(expenses_list):
                                    exp = ET.SubElement(tkt_expenses, ('Expense' + str(i)))
                                    exp.set('item', expense[0])
                                    exp.set('cost', expense[1])

        with open('file.xml', "wb") as fo:  # Must be 'wb', not 'w' in Python 3
            tree.write(fo)
