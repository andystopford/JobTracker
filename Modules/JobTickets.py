from PyQt5 import QtCore, QtGui, QtWidgets


class JobTickets(QtWidgets.QListWidget):
    def __init__(self, parent):
        super().__init__(parent)
        """Displays list of job tickets"""
        self.parent = parent
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        #self.connect(self, QtCore.SIGNAL("customContextMenuRequested(QPoint)"),
        #             self.rclick_menu)
        self.itemActivated.connect(self.select_ticket)
        self.itemDoubleClicked.connect(self.rename_ticket)

    def contextMenuEvent(self, event):
        menu = QtWidgets.QMenu(self)
        delete = QtWidgets.QAction('Delete', self)
        menu.addAction(delete)
        menu.popup(QtGui.QCursor.pos())
        delete.triggered.connect(self.delete_entry)

    def select_ticket(self):
        """By clicking item or from JT.display_tickets()"""
        self.parent.ui.ticketNotes.load_text()
        self.parent.ui.hoursTable.fill_table()
        self.parent.ui.expensesTable.fill_table()
        self.parent.ui.paymentTable.fill_table()
        self.parent.load_tracks()
        self.parent.enable_day()
        self.parent.display_job()
        # font = QtGui.QFont()
        # font.setBold(True)
        # e.setFont(font)

    def rename_ticket(self, item):
        """If lamda is not used, self.ticket_changed(item_name) will be
        immediately evaluated and then the result passed by the connect method.
        With lambda, the interpreter knows to pass item_name to be evaluated
        subsequently"""
        item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable |
                      QtCore.Qt.ItemIsEnabled)
        item_name = item.text()
        self.itemChanged.connect(lambda: self.tkt_name_changed(item_name))

    def tkt_name_changed(self, old_name):
        """Double click to change name"""
        curr_item = self.currentItem()
        day = self.parent.get_day()
        ticket_list = day[0].get_ticket_list(day[1], day[2])
        self.parent.ui.menu_curr_tickets.clear()
        for tkt in ticket_list:
            if tkt.get_name() == old_name:
                tkt.set_name(curr_item.text())
        self.parent.timer.fill_menu()
        self.parent.dirty = True

    def delete_entry(self):
        row_index = self.currentRow()
        self.parent.ui.ticketNotes.clear()
        self.parent.ui.hoursTable.clear()
        self.parent.ui.expensesTable.clear()
        self.takeItem(row_index)
        day = self.parent.get_day()
        model = day[0]
        model.delete_ticket(day[1], day[2], row_index)
        self.parent.explorer.refresh_today()
        self.parent.dirty = True




