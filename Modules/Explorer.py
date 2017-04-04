import sys

from PyQt4 import QtCore, QtGui

sys.path.append("./UI")
from Explorer_UI import Explorer_Ui


class Explorer(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent, QtCore.Qt.WindowStaysOnTopHint)
        self.ui = Explorer_Ui()
        self.ui.setup_ui(self)
        self.resize(400, 500)
        self.setWindowTitle("JobTracker Explorer")
        self.parent = parent
        # TODO This path is for testing only!
        self.user_path = "/home/andy/Projects/Programming/Python/JobTracker2/JobTrackerUser/"
        # Signals
        self.ui.search_button.clicked.connect(self.search)
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

    def search(self):
        """Searches tickets for entered text"""
        search_list = self.parent.model.search_list
        del search_list[:]
        word_list = []
        model = self.parent.model
        search_word = str(self.ui.search_box.toPlainText())
        for item in search_word.split():
            word_list.append(item)
        for row in range(12):
            for col in range(37):
                day_item = model.item(row, col)
                if day_item.child(0, 1):
                    if day_item.child(0, 1).data():
                        tickets = day_item.child(0, 1).data()
                        for ticket in tickets:
                            # Now filter YearView highlighting
                            name = ticket.get_name()
                            notes = ticket.get_notes()
                            for item in word_list:
                                if item.lower() in name.lower():
                                    #print('name', name)
                                    search_list.append(ticket)
                                if notes:
                                    if item.lower() in notes.lower():
                                        #print(notes)
                                        search_list.append(ticket)
        for item in search_list:
            print(item.get_name())
        self.parent.model.set_year(self.parent.year, False)


    def search_tkt_cat(self, cat):
        if self.ui.rem_chkBox.isChecked():
            if cat == 'Removal':
                return True
        if self.ui.wrk_chkBox.isChecked():
            if cat == 'Work':
                return True
        if self.ui.othr_chkBox.isChecked():
            if cat == 'Other':
                return True
        else:
            return False


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