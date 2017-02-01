from PyQt4 import QtCore, QtGui, Qt


class DateDisplay(QtGui.QStyledItemDelegate):
    def __init__(self, parent):
        """Colour codes any days with existing GPS files and fills in date text"""
        super(DateDisplay, self).__init__(parent)
        self.date_list =[]
        self.log_list = []
        self.parent = parent

    def setup(self, date_list, log_list):
        self.date_list = date_list
        self.log_list = log_list

    def paint(self, painter, option, index):
        super(DateDisplay, self).paint(painter, option, index)
        horiz_header = self.parent.horizontalHeader()
        cell_x = horiz_header.sectionSize(0)
        vert_header = self.parent.verticalHeader()
        cell_y = vert_header.sectionSize(0)
        pen = QtGui.QPen()
        painter.setPen(pen)
        # Point positions for colour coded fills
        # Top left triangle
        left_tri1 = QtCore.QPoint(option.rect.x() + cell_x, option.rect.y())
        left_tri2 = QtCore.QPoint(option.rect.x(), option.rect.y())
        left_tri3 = QtCore.QPoint(option.rect.x(), option.rect.y() + cell_y)

        for date in self.date_list:
            row = date[1]  # month
            col = date[0]  # log_date
            text = date[2]  # text to fill in
            if index.row() == row and index.column() == col:
                # Fill in dates
                date_pos = QtCore.QPoint(option.rect.x() + cell_x * 0.4, option.rect.y() + cell_y * 0.7)
                painter.save()
                painter.setRenderHint(painter.Antialiasing)
                # Fill in colour codes - log_date[0] = log_date, log_date[1] = month.
                for log_date in self.log_list:
                    painter.setPen(Qt.Qt.NoPen)
                    if str(log_date[0]) == date[2] and log_date[1] == date[1] + 1:
                        # Invoke draw_top_left_triangle()
                        triangle = self.draw_top_left_triangle([left_tri1, left_tri2, left_tri3])
                        painter.setBrush(triangle[1])
                        painter.drawPolygon(triangle[0])

                # Draw date text - must go last to be on top
                painter.setPen((QtGui.QColor(0, 0, 0)))
                painter.drawText(date_pos, text)
                painter.restore()

    def draw_top_left_triangle(self, points):
        """For GPS tracks"""
        tri = QtGui.QPolygon(points)
        colour = QtGui.QColor(255, 150, 150)
        return tri, colour


