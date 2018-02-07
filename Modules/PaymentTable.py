from PyQt4 import QtGui


class PaymentTable(QtGui.QTableWidget):
    """Table where payments can be added/displayed for selected job ticket"""
    def __init__(self, parent):
        super(PaymentTable, self).__init__(parent)
        self.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.parent = parent
        self.init()

    def init(self):
        payment = QtGui.QTableWidgetItem()
        amount = QtGui.QTableWidgetItem()
        self.setItem(0, 0, payment)
        self.setItem(0, 1, amount)
        self.setHorizontalHeaderLabels(['Payment', 'Amount'])

    def fill_table(self):
        """on selecting ticket, sets up table and fills from ticket's
        payment data"""
        self.init()
        ticket = self.parent.get_ticket()
        paid = ticket.get_payment()
        if paid:
            self.item(0, 0).setText(paid[0])
            self.item(0, 1).setText(paid[1])

    def update(self):
        """Adds payment to current ticket"""
        payment = self.item(0, 0).text()
        amount = self.item(0, 1).text()
        paid = [payment, amount]
        ticket = self.parent.get_ticket()
        ticket.set_payment(paid)
        self.parent.dirty = True

        # TODO warning colour for un-saved cells?