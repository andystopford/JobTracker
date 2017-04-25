import sys

from PyQt4 import QtCore, QtGui

sys.path.append("./UI")
from Explorer_UI import Explorer_Ui


class Explorer(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent, QtCore.Qt.WindowStaysOnTopHint)
        self.ui = Explorer_Ui()
        self.ui.setup_ui(self)
        #self.resize(400, 500)
        self.setWindowTitle("JobTracker Explorer")
        self.parent = parent
        # TODO This path is for testing only!
        self.user_path = "/home/andy/Projects/Programming/Python/JobTracker2/JobTrackerUser/"
        # Signals
        self.ui.name_clear_button.clicked.connect(self.clear_names)
        self.ui.notes_clear_button.clicked.connect(self.clear_notes)
        self.ui.name_search_button.clicked.connect(self.search_name)
        self.ui.notes_search_button.clicked.connect(self.search_notes)
        self.ui.filter_clr_butn.clicked.connect(self.clear_all)
        self.ui.rem_chkBox.stateChanged.connect(self.chkBox_changed)
        self.ui.wrk_chkBox.stateChanged.connect(self.chkBox_changed)
        self.ui.othr_chkBox.stateChanged.connect(self.chkBox_changed)
        self.ui.rem_chkBox.setChecked(True)
        self.ui.wrk_chkBox.setChecked(True)
        self.ui.othr_chkBox.setChecked(True)

    def test(self):
        print('Search pressed')

    def chkBox_changed(self):
        try:
            self.parent.model.set_year(self.parent.year, False)
        except AttributeError:
            # Occurs on startup before a model has been initialised
            return

    def search_name(self):
        self.search('name')

    def search_notes(self):
        self.search('notes')

    def search(self, type):
        """Searches tickets for entered text"""
        if type == 'name':
            del self.parent.model.name_search_list[:]
        if type == 'notes':
            del self.parent.model.notes_search_list[:]
        name_word_list = []
        notes_word_list = []
        model = self.parent.model
        name_search = str(self.ui.name_search_box.toPlainText())
        notes_search = str(self.ui.notes_search_box.toPlainText())
        for item in name_search.split():
            name_word_list.append(item)
        for item in notes_search.split():
            notes_word_list.append(item)
        for row in range(12):
            for col in range(37):
                day_item = model.item(row, col)     # i.e. a day QItem
                if day_item.child(0, 1):
                    if day_item.child(0, 1).data():
                        tickets = day_item.child(0, 1).data()
                        for ticket in tickets:
                            # Is the cat filter on?
                            cats = self.check_cat_checked()
                            for cat in cats:
                                if ticket.get_cat() == cat:
                                    # Now filter YearView highlighting
                                    name = ticket.get_name()
                                    notes = ticket.get_notes()
                                    for item in name_word_list:
                                        # This is the bit that doesn't work properly:
                                        if item.lower() in name.lower():
                                            self.parent.model.name_search_list.append(day_item)
                                    for item in notes_word_list:
                                        if notes:
                                            if item.lower() in notes.lower():
                                                #print(row, col, name, day_item)
                                                #print(notes)
                                                self.parent.model.notes_search_list.append(day_item)
        self.parent.model.set_year(self.parent.year, False)

    def check_cat_checked(self):
        checked_list = []
        if self.ui.rem_chkBox.isChecked():
            checked_list.append('Removal')
        if self.ui.wrk_chkBox.isChecked():
            checked_list.append('Work')
        if self.ui.othr_chkBox.isChecked():
            checked_list.append('Other')
        return checked_list

    def clear_names(self):
        self.ui.name_search_box.clear()
        del self.parent.model.name_search_list[:]
        self.parent.model.set_year(self.parent.year, False)

    def clear_notes(self):
        self.ui.notes_search_box.clear()
        del self.parent.model.notes_search_list[:]
        self.parent.model.set_year(self.parent.year, False)

    def clear_all(self):
        self.ui.name_search_box.clear()
        self.ui.notes_search_box.clear()
        del self.parent.model.name_search_list[:]
        del self.parent.model.notes_search_list[:]
        self.parent.model.set_year(self.parent.year, False)


class QColorButton(QtGui.QPushButton):
    """Custom Qt Widget to show a chosen color.
    Left-clicking the button shows the color-chooser, while
    right-clicking resets the color to None (no-color).
    """
    colorChanged = QtCore.pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(QColorButton, self).__init__(*args, **kwargs)

        self._color = None
        self.setMaximumWidth(32)
        self.pressed.connect(self.onColorPicker)

    def setColor(self, color):
        if color != self._color:
            self._color = color
            self.colorChanged.emit()

        if self._color:
            self.setStyleSheet("background-color: %s;" % self._color)
        else:
            self.setStyleSheet("")

    def color(self):
        return self._color

    def onColorPicker(self):
        '''
        Show color-picker dialog to select color.

        Qt will use the native dialog by default.

        '''
        dlg = QtGui.QColorDialog(self)
        if self._color:
            dlg.setCurrentColor(QtGui.QColor(self._color))

        if dlg.exec_():
            self.setColor(dlg.currentColor().name())

    def mousePressEvent(self, e):
        if e.button() == QtCore.Qt.RightButton:
            self.setColor(None)

        return super(QColorButton, self).mousePressEvent(e)