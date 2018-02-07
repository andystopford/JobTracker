from transitions import Machine


class StateMachine:
    def __init__(self, parent):
        """A state machine to save notes from ticketNotes whenever the day or
        ticket selection is changed"""
        self.parent = parent
        self.states = ['empty', 'tkt_issued', 'unsaved_text', 'saved_text']
        # Set initial state
        self.machine = Machine(model=self, states=self.states, initial='empty')
        # add_ticket ##################################
        # Add a ticket
        self.machine.add_transition(trigger='add_ticket', source='empty', dest='tkt_issued', after='ticket_issued')

        # New ticket - save text
        self.machine.add_transition(trigger='add_ticket', source='unsaved_text', dest='tkt_issued', after='save_text')

        # Switch ticket selection without entering text
        self.machine.add_transition(trigger='add_ticket', source='tkt_issued', dest='tkt_issued', after='ticket_issued')

        # text_entered ################################
        # Text entered
        self.machine.add_transition(trigger='text_entered', source='tkt_issued', dest='unsaved_text', after='unsaved')

        # Text entered when unsaved text present
        self.machine.add_transition(trigger='text_entered', source='unsaved_text', dest='unsaved_text', after='unsaved')

        # Prevent error messages when switching date due to clear() op in
        # ticketNotes.save()
        self.machine.add_transition(trigger='text_entered', source='empty', dest='empty')

        # new_date #####################################
        # Now add transition to save, and return to initial state on date change
        self.machine.add_transition(trigger='new_date', source='unsaved_text', dest='empty', after='save_text')

        # Changed date when no text entered
        self.machine.add_transition(trigger='new_date', source='tkt_issued', dest='empty', after='date_changed')

        # Transition when no save required
        self.machine.add_transition(trigger='new_date', source='empty', dest='empty', after='clean_date')

        # use_ticket ###################################
        # Transition when existing ticket selected
        self.machine.add_transition(trigger='use_ticket', source='unsaved_text', dest='tkt_issued', after='load_ticket')

    def ticket_issued(self):
        print('Ticket issued')
        print(self.state)
        print('')
        self.parent.ui.ticketNotes.clear()
        self.parent.ui.ticketNotes.load_text()

    def load_ticket(self):
        print('Ticket loaded')
        print(self.state)
        print('')
        self.parent.ui.ticketNotes.save()
        self.parent.ui.ticketNotes.load_text()

    def save_text(self):
        # Save and clear text
        print('Saving text and returning to empty')
        print(self.state)
        print('')
        self.parent.ui.ticketNotes.save()

    def date_changed(self):
        print('Date changed - now empty')
        print(self.state)
        print('')
        self.parent.ui.ticketNotes.save()
        self.parent.ui.ticketNotes.clear()

    def unsaved(self):
        """For debug only"""
        text = self.parent.ui.ticketNotes.toPlainText()
        print('Unsaved text', text)
        print(self.state)
        print('')

    def clean_date(self):
        """For debug only"""
        print('New date')
        print(self.state)
        print('')


