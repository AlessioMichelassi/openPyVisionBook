import logging

from PyQt6.QtCore import *
from PyQt6.QtGui import *

from cap5.mainDir.inputDevice.baseDevice.inputDevice_Base import InputDevice
from cap5.mainDir.inputDevice.captureDevice.captureWidget.desktopCaptureWidget import DesktopCaptureWidget
from cap5.mainDir.inputDevice.captureDevice.inputObject.desktopCapture import DesktopCapture


class InputDevice_DesktopCapture(InputDevice):
    """
        An InputDevice is any input of the mixer.
        It put together the thread, the input object and the graphic interface
        and act as interface to the mixer
        """

    def __init__(self, name, parent=None):
        super().__init__(name, parent)
        self.active = False
        self.graphicInterface = DesktopCaptureWidget()
        self.graphicInterface.typeChanged.connect(self.onTypeChanged)
        self.currentDesktopType = "initDesktop"
        self.currentParams = {
            "screenIndex": 0,
            "screenRegion": (0, 0, 1920, 1080)
        }
        self.updateInputObject(self.currentDesktopType, self.currentParams)

    def updateInputObject(self, desktopType, params):
        print(f"Updating input object to noise type: {desktopType} with params: {params}")
        if self._thread and self._thread.isRunning():
            self.stop()
        if desktopType == "initDesktop":
            return
        else:
            inputObject = DesktopCapture(params['screenRegion'])
            inputObject.init_camera(params['screenIndex'])

        self.setInputObject(inputObject)

    def onTypeChanged(self, data):
        desktopType = data.get('type', 'initDesktop')
        print(f"*** Desktop Type Changed to {desktopType} ***")
        self.currentDesktopType = desktopType
        self.currentParams = data.get('params', {})
        self.updateInputObject(desktopType, self.currentParams)

    def onParamsChanged(self, data):
        pass

    def serialize(self):
        """
        Serializes the current state of the input device (Noise generator) into a dictionary.
        """
        data = super().serialize()  # Call the base class method
        data.update({
            "name": self._name,
            "type": "DesktopCapture",
            "params": self.currentParams
        })
