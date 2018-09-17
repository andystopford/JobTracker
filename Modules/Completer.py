#!/usr/bin/env python
import DarkStyle
from PyQt5 import QtCore, QtWidgets


class Completer(QtWidgets.QCompleter):
    def __init__(self, parent):
        """Completer for the job_name_box which suggests job names from the
        current year"""
        super().__init__(parent)
        self.parent = parent
        self.setCompletionMode(QtWidgets.QCompleter.PopupCompletion)
        self.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        model = QtCore.QStringListModel()
        model.setStringList(self.get_job_list())
        self.setModel(model)
        self.popup().setStyleSheet(DarkStyle.load_stylesheet_pyqt5())

    def get_job_list(self):
        """Get a list of all job names ffor the current year"""
        model = self.parent.model
        job_list = []
        for row in range(12):
            for col in range(37):
                day_item = model.item(row, col)  # i.e. a day QItem
                if day_item.child(0, 1):
                    if day_item.child(0, 1).data():
                        tickets = day_item.child(0, 1).data()
                        for ticket in tickets:
                            job = ticket.get_job()
                            if job:
                                if job not in job_list:
                                    job_list.append(job)
        return job_list

