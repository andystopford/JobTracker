from PyQt4 import QtGui


class PaymentTable(QtGui.QTableWidget):
    def __init__(self, parent):
        super(PaymentTable, self).__init__(parent)
        self.parent = parent
        self.init()

    def init(self):
        payment = QtGui.QTableWidgetItem()
        amount = QtGui.QTableWidgetItem()
        self.setItem(0, 0, payment)
        self.setItem(0, 1, amount)
        self.setHorizontalHeaderLabels(['Payment', 'Amount'])

    def fill_table(self):
        """"""
        self.init()
        ticket = self.parent.get_ticket()
        paid = ticket.get_payment()
        if paid:
            self.item(0, 0).setText(paid[0])
            self.item(0, 1).setText(paid[1])
            #payment = QtGui.QTableWidgetItem(paid[0])
            #self.setItem(0, 0, payment)
            #self.setItem(0, 1, amount)
            #item = self.ui.payment_table.itemAt(0, 0).text()
            #amount = self.ui.payment_table.itemAt(0, 1).text()

    def update(self):
        """"""
        payment = self.item(0, 0).text()
        amount = self.item(0, 1).text()
        paid = [payment, amount]
        ticket = self.parent.get_ticket()
        ticket.set_payment(paid)
        self.parent.dirty = True

        # TODO warning colour for un-saved cells?