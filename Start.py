#!/usr/bin/python3.4
import sys

from PyQt4 import QtGui, Qt

from JobTracker import MainWindow

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    splash_pix = QtGui.QPixmap("./Icons/icon_start.png")
    splash = QtGui.QSplashScreen(splash_pix, Qt.Qt.WindowStaysOnTopHint)
    splash.setMask(splash_pix.mask())
    splash.show()
    app.processEvents()
    myapp = MainWindow()
    myapp.show()
    splash.finish(myapp)
    sys.exit(app.exec_())