from PyQt6.QtCore import pyqtSignal

from cap5.cap5_3.videoHub.inputDevice.baseDevice.inputDevice_Base import InputDevice
from cap5.cap5_3.videoHub.inputDevice.generatorDevice.generatorWidget.smpteGeneratorWidget import SmpteGeneratorWidget
from cap5.mainDir.inputs.generator.generator_SMPTE import SMPTEBarsGenerator


class InputDevice_SmpteGenerator(InputDevice):
    """
    An InputDevice is any input of the mixer.
    It put together the thread, the input object and the graphic interface
    and act as interface to the mixer
    """

    def __init__(self, name, parent=None):
        super().__init__(name, parent)
        self._frame = None
        # set the input type
        self.setInputObject(SMPTEBarsGenerator())
        # set the graphic interface
        self.graphicInterface = SmpteGeneratorWidget(self._input_object)
        # Connect the parametersChanged signal from the widget to handle updates
        self.graphicInterface.paramsChanged.connect(self.onParametersChanged)

    def updateInputObject(self, inputType):
        if inputType == "Smpte":
            # Actually there are only one type of Smpte Bars
            pass

    def onParametersChanged(self, data):
        """
        Handle the event when the parameters in the graphical interface change.
        This method is called whenever the widget emits the parametersChanged signal.
        """
        print("*** Smpte Generator Parameters Changed ***")
        inputType = data['smpteType']
        self.updateInputObject(inputType)
        print(f"Smpte type updated: {data}")

    def serialize(self):
        """
        This serializes the input object in a dictionary
        Pratically get the variables and put them in a dictionary
        :return:
        """
        data = super().serialize()  # Chiama il metodo della classe base
        return data

    def deserialize(self, data):
        """
        Deserialize the input object from a dictionary
        Pratically fill the variables with the data from the dictionary
        :param data:
        :return:
        """
        super().deserialize(data)
        self._name = data["name"]
