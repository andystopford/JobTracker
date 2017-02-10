from PyQt4 import QtCore, QtGui


class JobTickets(QtGui.QListWidget):
    def __init__(self, parent):
        super(JobTickets, self).__init__(parent)
        """Displays list of job tickets"""
        self.parent = parent
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.connect(self, QtCore.SIGNAL("customContextMenuRequested(QPoint)"), self.rclick_menu)
        self.itemActivated.connect(self.select_ticket)
        self.itemDoubleClicked.connect(self.rename_ticket)

    def select_ticket(self):
        """By clicking item"""
        self.parent.ui.ticketNotes.load_text()
        self.parent.ui.hoursTable.fill_table()
        self.parent.ui.expensesTable.fill_table()
        self.parent.load_tracks()

    def rename_ticket(self, item):
        """If lamda is not used, self.ticket_changed(item_name) will be immediately
        evaluated and then the result passed by the connect method. With lambda,
        the interpreter knows to pass item_name to be evaluated subsequently"""
        item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)
        item_name = item.text()
        self.itemChanged.connect(lambda: self.tkt_name_changed(item_name))

    def tkt_name_changed(self, old_name):
        """Double click to change name"""
        curr_item = self.currentItem()
        day = self.parent.get_day()
        ticket_list = day[0].get_ticket_list(day[1], day[2])
        for tkt in ticket_list:
            if tkt.get_name() == old_name:
                tkt.set_name(curr_item.text())
        self.parent.dirty = True

    def rclick_menu(self):
        menu = QtGui.QMenu(self)
        delete = QtGui.QAction('Delete', self)
        menu.addAction(delete)
        menu.popup(QtGui.QCursor.pos())
        delete.triggered.connect(self.delete_entry)

    def delete_entry(self):
        row_index = self.currentRow()
        self.parent.ui.ticketNotes.clear()
        self.parent.ui.hoursTable.clear()
        self.parent.ui.expensesTable.clear()
        self.takeItem(row_index)
        day = self.parent.get_day()
        model = day[0]
        model.delete_ticket(day[1], day[2], row_index)
        self.parent.dirty = True




