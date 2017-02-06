from PyQt4 import QtGui


class TicketNotes(QtGui.QTextEdit):
    def __init__(self, parent):
        super(TicketNotes, self).__init__(parent)
        self.parent = parent
        self.textChanged.connect(self.text_changed)
        self.buffer = ''
        self.curr_ticket = ''

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
        #print('loading text', ticket.get_name(), notes)

    def text_changed(self):
        """Changes to text trigger the stateMachine to 'unsaved_text'
        state and updates the buffer"""
        print('TN - Notes changed')
        #self.parent.stateMachine.text_entered()
        self.buffer = self.toPlainText()

    def save(self):
        """Save text from buffer to the previous ticket and
        sets self.curr_ticket to the selected ticket's name"""
        day = self.parent.get_day()     # returns model, row, col of seln.
        old_tkt = day[0].get_ticket(day[1], day[2], self.curr_ticket)
        print('day is ', day)
        print('curr_ticket is ', self.curr_ticket)
        tkt_list = day[0].get_ticket_list(day[1], day[2])
        print('tkt list ', tkt_list)
        name = tkt_list[0].get_name()
        print('name', name)
        text = self.buffer
        print('text being saved is ', text)
        if old_tkt:
            print('old ticket is ', old_tkt.get_name())
            print('TN - Saved')
            old_tkt.set_notes(text)
        else:
            tkt = day[0].get_ticket(day[1], day[2], name)
            print('ticket saving to ', name)
            tkt.set_notes(text)

        self.buffer = ''
        ticket = self.get_ticket()
        self.curr_ticket = ticket.get_name()
        self.clear()

