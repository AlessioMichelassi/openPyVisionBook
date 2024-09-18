import logging

from PyQt6.QtCore import *
from PyQt6.QtGui import *

from cap5.mainDir.inputDevice.baseDevice.inputDevice_Base import InputDevice
from cap5.mainDir.inputDevice.captureDevice.captureWidget.captureCameraWidget import CameraCaptureWidget
from cap5.mainDir.inputDevice.captureDevice.inputObject.videoCapture017 import VideoCapture017


class InputDevice_CameraCapture(InputDevice):
    """
        An InputDevice is any input of the mixer.
        It put together the thread, the input object and the graphic interface
        and act as interface to the mixer
        """

    def __init__(self, name, parent=None):
        super().__init__(name, parent)
        self.active = False
        self.graphicInterface = CameraCaptureWidget()
        self.graphicInterface.typeChanged.connect(self.onTypeChanged)
        self.cameraCaptureType = "initCapture"
        self.currentParams = {
            "cameraIndex": 0
        }
        self.updateInputObject(self.cameraCaptureType, self.currentParams)

    def updateInputObject(self, cameraType, params):
        print(f"Updating input object to noise type: {cameraType} with params: {params}")
        if self._thread and self._thread.isRunning():
            self.stop()
        if cameraType == "initCapture":
            return
        else:
            inputObject = VideoCapture017()
            inputObject.initCamera(params.get('cameraIndex', 0))
        self.setInputObject(inputObject)

    def onTypeChanged(self, data):
        captureType = data.get('type', 'cameraCapture')
        print(f"*** Desktop Type Changed to {captureType} ***")
        self.cameraCaptureType = captureType
        self.currentParams = data.get('params', {})
        self.updateInputObject(captureType, self.currentParams)

    def onParamsChanged(self, data):
        pass

    def serialize(self):
        """
        Serializes the current state of the input device (Noise generator) into a dictionary.
        """
        data = super().serialize()  # Call the base class method
        data.update({
            "name": self._name,
            "type": "CameraCapture",
            "params": self.currentParams
        })
