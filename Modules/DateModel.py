from PyQt4 import QtGui, QtCore, Qt


class DateModel(QtGui.QStandardItemModel):
    def __init__(self, parent):
        super(DateModel, self).__init__(parent)
        self.parent = parent

    def supportedDropActions(self):
        return QtCore.Qt.CopyAction | QtCore.Qt.MoveAction

    def add_ticket(self):
        """Builds a tree for a new Job Ticket"""
        rows = self.rowCount()
        ticket = QtGui.QStandardItem('Ticket ' + str(rows + 1))
        tracks = QtGui.QStandardItem('Tracks')
        hours = QtGui.QStandardItem('Hours')
        total_hours = QtGui.QStandardItem('Hours Total')
        costs = QtGui.QStandardItem('Costs')
        materials = QtGui.QStandardItem('Materials')
        total_miles = QtGui.QStandardItem('Miles Total')
        other_costs = QtGui.QStandardItem('Other Costs')
        notes = QtGui.QStandardItem('Notes')
        self.appendRow(ticket)
        ticket.insertRow(0, tracks)
        ticket.insertRow(1, hours)
        ticket.insertRow(2, costs)
        ticket.insertRow(3, notes)
        hours.insertRow(0, total_hours)
        costs.insertRow(0, total_miles)
        costs.insertRow(1, materials)
        costs.insertRow(2, other_costs)

    def dropMimeData(self, data, action, row, column, parent):
        """parent refers to this model's index, not the source"""
        #print('data', data)  # MimeData
        sel_item = self.item(parent.row(), parent.column())
        tracks = sel_item.child(0)
        curr_item = QtGui.QStandardItem('Track')
        tracks.insertRow(0, curr_item)
        src_model = self.parent.trackModel
        trk_data = []
        if data.hasFormat('application/x-qabstractitemmodeldatalist'):
            byte_array = data.data('application/x-qabstractitemmodeldatalist')
            src_row = self.decode_data(byte_array)
            event_list = ['Start ', 'End ', 'Hours ', 'Miles ']
            for i in range(0, 4):
                index = QtGui.QStandardItemModel.index(src_model, src_row, i)
                trk_item = src_model.itemFromIndex(index)
                brush = trk_item.background()
                trk_item = str(event_list[i] + trk_item.text())
                trk_item = QtGui.QStandardItem(trk_item)
                trk_data.append(trk_item)
            curr_item.appendColumn(trk_data)
            curr_item.setBackground(brush)
            return True

    def decode_data(self, byte_array):
        ds = QtCore.QDataStream(byte_array)
        row = ds.readInt32()  # gives correct row/col numbers
        return row

    def edit_item(self, index):
        """Adds QStandardItem (if not already present) to write/edit
        notes, etc"""
        item = self.itemFromIndex(index)
        notesDialogue = NotesDialogue()
        itxt = item.text()
        if itxt == 'Notes':
            if not item.hasChildren():
                result = notesDialogue.get_text()
                if result[1]:
                    notes = QtGui.QStandardItem(result[0])
                    item.insertRow(0, notes)
            else:
                child = item.child(0)
                text = child.text()
                result = notesDialogue.open_text(text)
                if result[1]:
                    child.setText(result[0])

        if itxt == 'Materials' or itxt == 'Other Costs':
            result = notesDialogue.get_table_view(self, index)
            if result[1]:
                rc = self.rowCount(index)
                item = self.itemFromIndex(index)
                print('row count', rc)
                # Clear existing rows
                if item.hasChildren():
                    item.removeRows(0, rc)
                # Enter new data from table
                for i, data_tuple in enumerate(result[0]):
                    cost_item = QtGui.QStandardItem(data_tuple[0])
                    cost = QtGui.QStandardItem(data_tuple[1])
                    item.insertRow(i, cost_item)
                    cost_item.insertRow(0, cost)
                    #print(data_tuple)

    def delete_item(self, index):
        item = self.itemFromIndex(index)


class NotesDialogue(QtGui.QDialog):
    def __init__(self, parent=None):
        """A popup dialogue to edit Job Tickets"""
        QtGui.QWidget.__init__(self, parent)
        layout = QtGui.QVBoxLayout()
        self.text_edit = QtGui.QTextEdit()
        self.table_view = QtGui.QTableView()
        hh = self.table_view.horizontalHeader()
        hh.setStretchLastSection(True)
        self.setLayout(layout)
        layout.addWidget(self.text_edit)
        layout.addWidget(self.table_view)
        # OK and Cancel buttons
        buttons = QtGui.QDialogButtonBox(
            QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel,
            Qt.Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def open_text(self, text):
        dialogue = NotesDialogue()
        dialogue.table_view.setVisible(False)
        dialogue.text_edit.setText(text)
        result = dialogue.exec_()
        text = dialogue.curr_text()
        return text, result == QtGui.QDialog.Accepted

    def get_text(self):
        dialogue = NotesDialogue()
        dialogue.table_view.setVisible(False)
        result = dialogue.exec_()
        text = dialogue.curr_text()
        return text, result == QtGui.QDialog.Accepted

    def curr_text(self):
        text = self.text_edit.toPlainText()
        return text

    def get_table_view(self, parent, index):
        dialogue = NotesDialogue()
        dialogue.text_edit.setVisible(False)
        tableModel = QtGui.QStandardItemModel()
        tableModel.setColumnCount(2)
        tableModel.setRowCount(2)
        parent_item = parent.itemFromIndex(index)
        labels = ['Item', 'Cost']
        tableModel.setHorizontalHeaderLabels(labels)

        if not parent_item.hasChildren():
            dialogue.table_view.setModel(tableModel)
        else:
            # Re-open existing data in table:
            rc = parent_item.rowCount()
            if rc == 2:
                tableModel.setRowCount(3)
            for i in range(0, rc):
                item = QtGui.QStandardItem(parent_item.child(i).text())
                cost = QtGui.QStandardItem(parent_item.child(i).child(0).text())
                tableModel.setItem(i, 0, item)
                tableModel.setItem(i, 1, cost)
            dialogue.table_view.setModel(tableModel)

        result = dialogue.exec_()
        rc = tableModel.rowCount()
        data_list = []
        for i in range(0, rc):
            r0 = tableModel.item(i, 0).text()
            r1 = tableModel.item(i, 1).text()
            row_data = (r0, r1)
            data_list.append(row_data)
        return data_list, result == QtGui.QDialog.Accepted


