
class StateMachine:
    def __init__(self, parent):
        self.parent = parent
        self.curr_day = ''
        self.prev_day = ''
        self.curr_ticket = ''
        self.prev_tkt = ''
        self.tkt_state = 'none'
        self.add_state = False  # No need to add text to ticket

    def set_curr_ticket(self, tkt):
        if self.tkt_state == 'none':
            # New ticket
            self.curr_day = self.parent.get_day()
            self.curr_ticket = tkt.text()
            self.tkt_state = 'new'
            if not self.add_state:
                self.parent.ui.ticketNotes.clear()
        if self.tkt_state == 'new':
            self.prev_tkt = self.curr_ticket
            self.curr_ticket = tkt.text()
            #
            if self.parent.ui.ticketNotes.get_changed():
                ticket = self.get_ticket(self.prev_tkt)
                notes = self.parent.ui.ticketNotes.save()
                ticket.set_notes(notes)
                self.parent.ui.ticketNotes.clear()
                self.parent.ui.ticketNotes.changed = False
            # Display saved notes:
            ticket = self.get_ticket(self.curr_ticket)
            notes = ticket.get_notes()
            self.parent.ui.ticketNotes.setText(notes)
        #print(self.prev_tkt)

    def check_unsaved(self):
        print('chk_uns')
        #print(self.parent.ui.ticketNotes.get_changed())
        if self.parent.ui.ticketNotes.get_changed():
            print('if')
            day = self.curr_day
            #print(day[1], day[2])
            #print(self.curr_ticket)
            notes = self.parent.ui.ticketNotes.save()
            ticket = day[0].get_ticket(day[1], day[2], self.curr_ticket)
            if ticket:
                print(ticket.get_name())
                ticket.set_notes(notes)
            else:
                print('none')
            self.parent.ui.ticketNotes.clear()
            self.parent.ui.ticketNotes.changed = False

            self.curr_day = self.parent.get_day()

    def get_ticket(self, tkt):
        day = self.parent.get_day()
        ticket = day[0].get_ticket(day[1], day[2], tkt)
        return ticket