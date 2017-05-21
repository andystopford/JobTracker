import os.path
import shutil
import sys
import xml.etree.ElementTree as ET

from PyQt4 import QtGui

sys.path.append("./Modules")
from Year import *
from Ticket import Track
from Model import*


class DataIO:
    def __init__(self, parent):
        """Module to read/write disc files"""
        self.path = './Logs'
        self.parent = parent
        # TODO This path is for testing only!
        self.user_path = "/home/andy/Projects/Programming/Python/JobTracker2/JobTrackerUser/"

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
        """Open user data"""
        try:
            path = self.user_path
            print(path + 'years.xml')
            with open(path + 'years.xml', "r") as fo:
                tree = ET.parse(fo)
                root = tree.getroot()
                for date in root:
                    year = date.get('date')
                    year = int(year[6:10])
                    row = int(date.get('row'))
                    col = int(date.get('col'))
                    if year not in self.parent.model_dict:
                        model = Model(self.parent)
                        model.set_year(year, True)
                        self.parent.model_dict[year] = model
                    model = self.parent.model_dict[year]
                    for tkt in date:
                        name = tkt.text
                        cat = tkt[0].text
                        # Comment out the following for first use:
                        job = tkt[1].text
                        notes = tkt[2].text
                        tracks = tkt[3]
                        ticket = model.add_ticket(row, col, cat)
                        ticket.set_name(name)
                        ticket.set_job(job)
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
                        expenses = tkt[4]
                        for exp in expenses:
                            item = exp.get('item')
                            cost = exp.get('cost')
                            expense = [item, cost]
                            ticket.add_expense(expense)
                        payment = tkt[5]
                        amnt = payment.get('Amount')
                        pmnt = payment.get('payment')
                        ticket.set_payment([pmnt, amnt])
        except:
            print('User not found')
        self.parent.clear_year()

    def save(self, model_dict):
        """Save user data"""
        # Might need something for following line
        #self.parent.ui.hoursTable.update_tracks()
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
                                job = tkt.get_job()
                                notes = tkt.get_notes()
                                track_list = tkt.get_tracks()
                                expenses_list = tkt.get_expenses()
                                payment = tkt.get_payment()
                                # Set ET sub-elements
                                tkt_name = ET.SubElement(tkt_date, "Name")
                                tkt_cat = ET.SubElement(tkt_name, 'Cat')
                                tkt_job = ET.SubElement(tkt_name, 'Job')
                                tkt_notes = ET.SubElement(tkt_name, 'Notes')
                                tkt_tracks = ET.SubElement(tkt_name, 'Tracks')
                                tkt_expenses = ET.SubElement(tkt_name, 'Expenses')
                                tkt_payment = ET.SubElement(tkt_name, 'Payment')
                                tkt_date.set('row', str(row))
                                tkt_date.set('col', str(col))
                                tkt_date.set('date', date)
                                tkt_name.text = name
                                tkt_cat.text = cat
                                tkt_notes.text = notes
                                tkt_payment.set('payment', payment[0])
                                tkt_payment.set('Amount', payment[1])
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
                                tkt_job.text = job
        path = self.user_path
        try:
            os.remove("{0}BAK_years.xml".format(path))
        except OSError as e:
            print(e.errno)
        os.rename("{0}years.xml".format(path), "{0}BAK_years.xml".format(path))
        with open("{0}years.xml".format(path), "wb") as fo:
            tree.write(fo)


