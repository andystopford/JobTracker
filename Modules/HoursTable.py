from PyQt4 import QtCore, QtGui
from Ticket import Track
from TimeConverter import*

class HoursTable(QtGui.QTableWidget):
    def __init__(self, parent):
        super(HoursTable, self).__init__(parent)
        self.setDragDropMode(QtGui.QAbstractItemView.DropOnly)
        self.parent = parent
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.connect(self, QtCore.SIGNAL("customContextMenuRequested(QPoint)"), self.rclick_menu)

    def rclick_menu(self):
        self.menu = QtGui.QMenu(self)
        add = QtGui.QAction('Add', self)
        delete = QtGui.QAction('Delete', self)
        self.menu.addAction(add)
        self.menu.addAction(delete)
        self.menu.popup(QtGui.QCursor.pos())
        add.triggered.connect(self.add_track)
        delete.triggered.connect(self.delete_track)

    def reset(self):
        self.setHorizontalHeaderLabels(['Start', 'End', 'Hours', 'Miles', 'Notes'])

    def dropEvent(self, event):
        src_model = event.source().parent.trackModel
        data = event.mimeData()
        trk = []   # list of times and distance
        if data.hasFormat('application/x-qabstractitemmodeldatalist'):
            byte_array = data.data('application/x-qabstractitemmodeldatalist')
            ticket = self.get_ticket()
            src_row = self.decode_data(byte_array)
            for i in range(0, 4):
                index = QtGui.QStandardItemModel.index(src_model, src_row, i)
                trk_item = src_model.itemFromIndex(index)
                brush = trk_item.background()
                trk_item = trk_item.text()
                trk.append(trk_item)
                #track = trk_data
            track = Track(trk[0], trk[1], trk[2], trk[3], '', brush, True)
            ticket.add_track(track)
        self.fill_table()

    def decode_data(self, byte_array):
        ds = QtCore.QDataStream(byte_array)
        row = ds.readInt32()  # gives correct row/col numbers
        return row

    def get_ticket(self):
        day = self.parent.get_day()
        tkt_name = self.parent.ui.job_tickets.currentItem()
        if not tkt_name:
            print('no ticket selected')# n.b. cope with changed notes for all
            return
        tkt_name = tkt_name.text()
        ticket = day[0].get_ticket(day[1], day[2], tkt_name)
        return ticket

    def fill_table(self):
        """Gets tracks for current ticket and fills table"""
        self.clear()
        self.reset()
        ticket = self.get_ticket()
        if ticket:
            track_list = ticket.get_tracks()
            row = 0
            self.setRowCount(len(track_list) + 1)
            for track in track_list:
                brush = track.get_brush()
                start = QtGui.QTableWidgetItem(track.get_start())
                start.setBackground(brush)
                self.setItem(row, 0, start)
                end = QtGui.QTableWidgetItem(track.get_end())
                end.setBackground(brush)
                self.setItem(row, 1, end)
                hours = QtGui.QTableWidgetItem(track.get_hours())
                hours.setBackground(brush)
                self.setItem(row, 2, hours)
                miles = QtGui.QTableWidgetItem(track.get_miles())
                miles.setBackground(brush)
                self.setItem(row, 3, miles)
                notes = QtGui.QTableWidgetItem(track.get_notes())
                notes.setBackground(brush)
                self.setItem(row, 4, notes)
                row += 1
        self.total()
        return

    def add_track(self):
        colour = QtGui.QColor(195, 218, 255)
        brush = QtGui.QBrush(colour)
        ticket = self.get_ticket()
        track = Track('', '', '00:00', '0', '', brush, False)
        ticket.add_track(track)
        self.clear()
        self.fill_table()

    def delete_track(self):
        ticket = self.get_ticket()
        row = int(self.currentRow())
        ticket.delete_track(row)
        self.clear()
        self.fill_table()

    def update_tracks(self):
        """Updates the current ticket with manually entered values and
        re-draws the table"""
        tc = TimeConverter()
        ticket = self.get_ticket()
        track_list = ticket.get_tracks()
        for t, track in enumerate(track_list):
            if not track.get_gps():
                # Init manually entered track
                new = []
                for i in range(0, 5):
                    new_val = (self.item(t, i)).text()
                    if i == 2:
                        new_val = tc.fix_lazy(new_val)
                    new.append(new_val)
                track.set_all(new[0], new[1], new[2], new[3], new[4])
            else:
                new_val = (self.item(t, 4)).text()
                track.set_notes(new_val)
        ticket.sort()
        self.clear()
        self.fill_table()
        self.total()

    def total(self):
        row_count = self.rowCount()
        tc = TimeConverter()
        total_hrs = 0
        total_miles = 0
        colour = QtGui.QColor(165, 151, 255)
        brush = QtGui.QBrush(colour)
        for i in range(0, row_count - 1):
            hrs = self.item(i, 2).text()
            hrs = tc.get_time_mins(hrs)
            total_hrs += hrs
        total_hrs = tc.get_time_hrs_mins(total_hrs)
        total_hours = QtGui.QTableWidgetItem()
        total_hours.setText(total_hrs)
        total_hours.setBackground(brush)
        self.setItem(row_count - 1, 2, total_hours)
        for i in range(0, row_count - 1):
            miles = float(self.item(i, 3).text())
            total_miles += miles
        total_dist = QtGui.QTableWidgetItem()
        total_dist.setText(str(total_miles))
        total_dist.setBackground(brush)
        self.setItem(row_count - 1, 3, total_dist)

