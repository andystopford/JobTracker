from PyQt4 import QtGui


class TicketNotes(QtGui.QTextEdit):
    def __init__(self, parent):
        super(TicketNotes, self).__init__(parent)
        self.parent = parent
        self.textChanged.connect(self.text_changed)
        self.changed = False

    def get_ticket(self):
        day = self.parent.get_day()
        tkt_name = self.parent.ui.job_tickets.currentItem()
        if not tkt_name:
            print('no ticket selected')
            return
        tkt_name = tkt_name.text()
        ticket = day[0].get_ticket(day[1], day[2], tkt_name)
        return ticket

    def get_old_ticket(self, old_tkt):
        day = self.parent.get_day()
        ticket = day[0].get_ticket(day[1], day[2], old_tkt)
        return ticket

    def text_changed(self):
        self.changed = True

    def get_changed(self):
        return self.changed

    def save(self):
        text = self.toPlainText()
        return text

    def update_ticket(self, ticket, text):
        print('z')
        ticket.set_notes(text)
        return

    def on_date_changed(self):
        if self.changed:
            tkt = self.get_ticket()
            name = tkt.get_name()
            print(name)
            self.clear()
        self.changed = True

    # TODO save/clear after date change