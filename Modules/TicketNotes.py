from PyQt4 import QtGui


class TicketNotes(QtGui.QTextEdit):
    def __init__(self, parent):
        """Editable field for job notes"""
        super(TicketNotes, self).__init__(parent)
        self.parent = parent

    def get_ticket(self):
        """Utility to get the current day's ticket"""
        day = self.parent.get_day()
        tkt_name = self.parent.ui.jobTickets.currentItem()
        if not tkt_name:
            #print('TN - no ticket selected')
            return
        tkt_name = tkt_name.text()
        ticket = day[0].get_ticket(day[1], day[2], tkt_name)
        return ticket

    def load_text(self):
        """Displays text from the current ticket """
        ticket = self.get_ticket()
        notes = ticket.get_notes()
        self.setText(notes)

    def save(self):
        """Saves current text to current ticket"""
        ticket = self.get_ticket()
        text = self.toPlainText()
        ticket.set_notes(text)
        self.parent.dirty = True



