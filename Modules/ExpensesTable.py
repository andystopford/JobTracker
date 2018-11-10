from decimal import *

from PyQt5 import QtCore, QtGui, QtWidgets


class ExpensesTable(QtWidgets.QTableWidget):
    def __init__(self, parent):
        """"""
        super().__init__(parent)
        self.parent = parent
        self.setRowCount(2)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        #self.connect(self, QtCore.SIGNAL("customContextMenuRequested"
        #                                 "(QPoint)"), self.rclick_menu)
        self.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)

    def contextMenuEvent(self, event):
        menu = QtWidgets.QMenu(self)
        delete = QtWidgets.QAction('Delete', self)
        menu.addAction(delete)
        menu.popup(QtGui.QCursor.pos())
        delete.triggered.connect(self.delete_entry)

    def delete_entry(self):
        row = int(self.currentRow())
        ticket = self.parent.get_ticket()
        exp = ticket.expenses_list[row]
        ticket.expenses_list.remove(exp)
        self.removeRow(row)
        self.setRowCount(len(ticket.expenses_list) + 1)
        self.total(ticket.expenses_list)
        self.parent.dirty = True

    def fill_table(self):
        ticket = self.parent.get_ticket()
        if ticket:
            exp_list = ticket.get_expenses()
            self.setRowCount(len(exp_list) + 1)
            for row, exp in enumerate(exp_list):
                item = QtWidgets.QTableWidgetItem(exp[0])
                self.setItem(row, 0, item)
                exp = QtWidgets.QTableWidgetItem(exp[1])
                self.setItem(row, 1, exp)
            self.total(exp_list)

    def update(self):
        ticket = self.parent.get_ticket()
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
        self.parent.dirty = True    # might not always be necessary

    def total(self, exp_list):
        row_count = self.rowCount()
        total_cost = Decimal(0.00).quantize(Decimal('.01'))
        for exp_item in exp_list:
            if len(exp_item) == 2:
                cost = Decimal(exp_item[1]).quantize(Decimal('.01'))
                total_cost += cost
        colour = QtGui.QColor(255, 159, 161)
        brush = QtGui.QBrush(colour)
        text_colour = QtGui.QColor('#1d1e1f')
        label = QtWidgets.QTableWidgetItem()
        label.setText('Total')
        label.setBackground(brush)
        label.setForeground(text_colour)
        total_cost_item = QtWidgets.QTableWidgetItem()
        total_cost_item.setText(str(total_cost))
        total_cost_item.setBackground(brush)
        total_cost_item.setForeground(text_colour)
        self.setItem(row_count - 1, 0, label)
        self.setItem(row_count - 1, 1, total_cost_item)
        self.insertRow(row_count - 1)
        self.setCurrentCell(row_count - 1, 0)


