from PyQt5.QtCore import pyqtSlot, pyqtSignal, QJsonValue

from .path import Path


class Polyline(Path):
    clicked = pyqtSignal(str)

    def __init__(self, latLngs, options=None):
        super().__init__()
        self.latLngs = latLngs
        self.options = options
        self._initJs()
        self._connectEventToSignal('clicked', '_onClick')

    def _initJs(self):
        leafletJsObject = 'L.polyline({latLngs}'.format(latLngs=self.latLngs)
        if self.options:
            leafletJsObject += ', {options}'.format(options=self.options)
        leafletJsObject += ')'
        self._createJsObject(leafletJsObject)

    @pyqtSlot(QJsonValue)
    def _onClick(self, event):
        """Trying to select polyline - not working"""
        print('ok')
        self.clicked.emit(event)


