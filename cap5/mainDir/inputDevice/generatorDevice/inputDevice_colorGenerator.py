import numpy as np

from cap5.mainDir.inputDevice.baseDevice.inputDevice_Base import InputDevice
from cap5.mainDir.inputDevice.generatorDevice.generatorWidget.colorGeneratorsWidget import ColorGeneratorWidget
from cap5.mainDir.inputDevice.generatorDevice.inputObject.generator_Color import ColorGenerator


class InputDevice_ColorGenerator(InputDevice):
    """
    An InputDevice is any input of the mixer.
    It put together the thread, the input object and the graphic interface
    and act as interface to the mixer
    """

    def __init__(self, name, parent=None):
        super().__init__(name, parent)
        self._frame = None
        self.setInputObject(ColorGenerator())
        # Set the graphical interface
        self.graphicInterface = ColorGeneratorWidget()
        # Connect the parametersChanged signal from the widget to handle updates
        self.graphicInterface.paramsChanged.connect(self.onParametersChanged)

    def updateInputObject(self, colorType):
        """
        Updates the input object based on the type selected from the UI.
        """
        if colorType == "rgb":
            self._input_object.setColor((0, 0, 0))
        elif colorType == "random":
            self._input_object.setColor((np.random.randint(0, 255),
                                         np.random.randint(0, 255),
                                         np.random.randint(0, 255)))
        elif colorType == "Black":
            self._input_object.setColor((0, 0, 0))

    def onParametersChanged(self, data):
        """
        Handle the event when the parameters in the graphical interface change.
        This method is called whenever the widget emits the parametersChanged signal.
        """
        print("*** Noise Generator Parameters Changed ***")
        colorType = data['colorType']
        if colorType == "rgb":
            self._input_object.setColor(data)
        elif colorType == "random":
            self._input_object.setColor((np.random.randint(0, 255),
                                         np.random.randint(0, 255),
                                         np.random.randint(0, 255)))
        elif colorType == "black":
            self._input_object.setColor((0, 0, 0))
        self.updateInputObject(colorType)

        print(f"Color type updated: {data}")

    def setColor(self, color):
        """
        Set the color of the input object
        :param color: the color to set
        """
        self._input_object.setColor(color)

    def serialize(self):
        """
        This serializes the input object in a dictionary
        Practically get the variables and put them in a dictionary
        :return:
        """
        data = super().serialize()  # Chiama il metodo della classe base
        return data

    def deserialize(self, data):
        """
        Deserialize the input object from a dictionary
        Practically fill the variables with the data from the dictionary
        :param data:
        :return:
        """
        super().deserialize(data)  # Chiama il metodo della classe base
        # Eventuale logica aggiuntiva se è necessario reimpostare parametri specifici
        self._name = data["name"]
        self.graphicInterface.updateInputObject()
