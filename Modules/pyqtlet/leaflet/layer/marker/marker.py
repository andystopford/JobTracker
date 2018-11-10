from PyQt5.QtCore import pyqtSlot, pyqtSignal, QJsonValue

from ..layer import Layer


class Marker(Layer):
    # These are the names of the signal being sent,
    # e.g. self.marker1.dragend.connect(self.dragged)
    dragend = pyqtSignal(str)
    pos = pyqtSignal(dict)

    def __init__(self, latLng, options=None, name=None, icon=None):
        super().__init__()
        self.name = name
        self.latLng = latLng
        self.options = options
        self.icon = icon
        self._initJs()
        self._connectEventToSignal('dragend', '_onDragend')

    def _initJs(self):
        leafletJsObject = 'L.marker({latLng}'.format(latLng=self.latLng)
        if self.options:
            leafletJsObject += ', {options}'.format(options=self.options)
        if self.icon:
            leafletJsObject += ', {icon}'.format(icon=self.icon)
        leafletJsObject += ')'
        self._createJsObject(leafletJsObject)

    def setIcon(self, icon):
        js = '{layerName}.setIcon({icon})'.format(layerName=self._layerName,
                                                  icon=icon)
        print(icon)
        self.runJavaScript(js)

    def setLatLng(self, latLng):
        js = '{layerName}.setLatLng({latLng})'.format(
                layerName=self._layerName, latLng=latLng)
        self.runJavaScript(js)

    def setOpacity(self, opacity):
        js = '{layerName}.setOpacity({opacity})'.format(
                layerName=self._layerName, opacity=opacity)
        self.runJavaScript(js)

    def getLatLng(self, callback):
        js = '{layerName}.getLatLng()'.format(
            layerName=self._layerName)
        self.getJsResponse(js, callback)

    def getOptions(self):
        return self.options

    def getLayerName(self):
        return self._layerName

    def getName(self):
        return self.name

    @pyqtSlot(QJsonValue)
    def _onDragend(self, event):
        name = self.getLayerName()
        self.dragend.emit(name)

