from PyQt5 import QtWidgets


class TicketNotes(QtWidgets.QTextEdit):
    def __init__(self, parent):
        """Editable field for job notes"""
        super().__init__(parent)
        self.parent = parent

    def load_text(self):
        """Displays text from the current ticket """
        ticket = self.parent.get_ticket()
        notes = ticket.get_notes()
        self.setText(notes)

    def save(self):
        """Saves current text to current ticket"""
        ticket = self.parent.get_ticket()
        text = self.toPlainText()
        if text:
            ticket.set_notes(text)
        self.parent.dirty = True



