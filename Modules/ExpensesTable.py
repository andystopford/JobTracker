from PyQt4 import QtCore, QtGui


class ExpensesTable(QtGui.QTableWidget):
    def __init__(self, parent):
        super(ExpensesTable, self).__init__(parent)
        self.parent = parent
        self.setRowCount(2)
        #self.itemSelectionChanged.connect(self.update)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.connect(self, QtCore.SIGNAL("customContextMenuRequested(QPoint)"), self.rclick_menu)

    def rclick_menu(self):
        self.menu = QtGui.QMenu(self)
        delete = QtGui.QAction('Delete', self)
        self.menu.addAction(delete)
        self.menu.popup(QtGui.QCursor.pos())
        delete.triggered.connect(self.delete_entry)

    def delete_entry(self):
        row = int(self.currentRow())
        ticket = self.get_ticket()
        exp = ticket.expenses_list[row]
        ticket.expenses_list.remove(exp)
        self.removeRow(row)
        self.setRowCount(len(ticket.expenses_list) + 1)
        self.total(ticket.expenses_list)

    def reset(self):
        self.setHorizontalHeaderLabels(['Item', 'Cost'])

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
        self.clear()
        self.reset()
        ticket = self.get_ticket()
        if ticket:
            exp_list = ticket.get_expenses()
            self.setRowCount(len(exp_list) + 1)
            for row, exp in enumerate(exp_list):
                item = QtGui.QTableWidgetItem(exp[0])
                self.setItem(row, 0, item)
                exp = QtGui.QTableWidgetItem(exp[1])
                self.setItem(row, 1, exp)
            self.total(exp_list)

    def update(self):
        ticket = self.get_ticket()
        ticket.expenses_list = []
        for row in range(self.rowCount() - 1):
            exp_item = []
            if self.item(row, 0):
                if self.item(row, 0).text() != 'Total':
                    exp_item.append(self.item(row, 0).text())
                    if self.item(row, 1):
                        exp_item.append(self.item(row, 1).text())
                    ticket.expenses_list.append(exp_item)
        self.total(ticket.expenses_list)

    def total(self, exp_list):
        row_count = self.rowCount()
        total_cost = 0.00
        for item in exp_list:
            if len(item) == 2:
                total_cost += float(item[1])
        #print(total_cost)
        #print('row count', row_count)
        #print(exp_list)
        colour = QtGui.QColor(255, 159, 161)
        brush = QtGui.QBrush(colour)
        label = QtGui.QTableWidgetItem()
        label.setText('Total')
        label.setBackground(brush)
        total_cost_item = QtGui.QTableWidgetItem()
        total_cost_item.setText(str(total_cost))
        total_cost_item.setBackground(brush)
        self.setItem(row_count - 1, 0, label)
        self.setItem(row_count - 1, 1, total_cost_item)
        self.insertRow(row_count - 1)
        self.setCurrentCell(row_count - 1, 0)


