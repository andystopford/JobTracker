#!/usr/bin/python3.6
import sys

from PyQt5 import QtGui, Qt
from PyQt5.QtWidgets import QApplication, QSplashScreen

from JobTracker import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    splash_pix = QtGui.QPixmap("./Icons/icon_start.png")
    splash = QSplashScreen(splash_pix, Qt.Qt.WindowStaysOnTopHint)
    splash.setMask(splash_pix.mask())
    splash.show()
    app.processEvents()
    myapp = MainWindow()
    myapp.show()
    splash.finish(myapp)
    sys.exit(app.exec_())