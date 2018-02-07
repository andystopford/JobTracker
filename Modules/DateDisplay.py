from PyQt4 import QtCore, QtGui, Qt


class DateDisplay(QtGui.QStyledItemDelegate):
    def __init__(self, parent):
        """Colour codes any days from existing GPS files and fills in
        date text
        """
        super(DateDisplay, self).__init__(parent)
        self.date_list =[]
        self.log_list = []
        self.parent = parent
        self.today_row = 0
        self.today_col = 0
        self.today = True

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
        # Point positions for cells
        point1 = QtCore.QPoint(option.rect.x() + (cell_x - 1), option.rect.y())
        point2 = QtCore.QPoint(option.rect.x(), option.rect.y())
        point3 = QtCore.QPoint(option.rect.x(), option.rect.y() + (cell_y - 1))
        point4 = QtCore.QPoint(option.rect.x() + (cell_x - 1), option.rect.y()
                               + (cell_y - 1))

        for date in self.date_list:
            row = date[1]  # month
            col = date[0]  # log_date
            text = date[2]  # text to fill in
            if index.row() == row and index.column() == col:
                # Fill in dates
                date_pos = QtCore.QPoint(option.rect.x() + cell_x * 0.4,
                                         option.rect.y() + cell_y * 0.7)
                painter.save()
                painter.setRenderHint(painter.Antialiasing)
                # Fill in colour codes - log_date[0] = log_date,
                # log_date[1] = month.
                for log_date in self.log_list:
                    painter.setPen(Qt.Qt.NoPen)
                    if str(log_date[0]) == date[2] and log_date[1] == date[1] \
                            + 1:
                        # Invoke draw_triangle_left()
                        triangle = self.draw_triangle_left([point1, point2,
                                                            point3])
                        painter.setBrush(triangle[1])
                        painter.drawPolygon(triangle[0])
                # Draw date text - must go last to be on top
                painter.setPen((QtGui.QColor('#0a0a0b')))
                if self.today:
                    if self.today_row == row:
                        if self.today_col == col:
                            # Set text colour for today
                            #pen.setWidth(15)
                            painter.setPen((QtGui.QColor(255, 0, 0)))
                            painter.setFont(QtGui.QFont("AnyStyle", -1, 75))
                            #outline = self.draw_outline([point1, point2,
                            # point3, point4])
                            #painter.drawPolygon(outline[0])
                painter.drawText(date_pos, text)
                painter.restore()

    def draw_triangle_left(self, points):
        """For GPS tracks"""
        tri = QtGui.QPolygon(points)
        colour = QtGui.QColor(159, 159, 161)
        return tri, colour
    
    def draw_outline(self, points):
        """For highlighting today"""
        outline = QtGui.QPolygon(points)
        colour = QtGui.QColor(255, 0, 0)
        return outline, colour

    def mark_today(self, row, col, is_true):
        """Identifies today and enables outlining"""
        self.today_row = row
        self.today_col = col
        self.today = is_true
