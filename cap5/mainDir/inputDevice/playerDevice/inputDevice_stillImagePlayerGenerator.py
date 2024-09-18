from cap5.mainDir.inputDevice.baseDevice.inputDevice_Base import InputDevice
from cap5.mainDir.inputDevice.playerDevice.playerWidget.stillImagePlayerWidget import StillImagePlayerWidget
from cap5.mainDir.inputDevice.playerDevice.inputObject.player_StillImage import StillImagePlayer


class InputDevice_StillImagePlayer(InputDevice):
    """
    An InputDevice for managing the Still Image Player.
    It combines the input object, the thread, and the graphical interface to act as the interface for the mixer.
    """

    def __init__(self, name, parent=None):
        super().__init__(name, parent)
        self._frame = None
        # Set the input object as StillImagePlayer
        self.setInputObject(StillImagePlayer(""))
        # Set the graphical interface
        self.graphicInterface = StillImagePlayerWidget()
        # Connect the parametersChanged signal from the widget to handle updates
        self.graphicInterface.typeChange.connect(self.onTypeChanged)
        self.graphicInterface.paramsChanged.connect(self.onParamsChanged)

    def onTypeChanged(self):
        pass

    def onParamsChanged(self, data):
        """
        Handle the event when the parameters in the graphical interface change.
        This method is called whenever the widget emits the parametersChanged signal.
        """
        if "imagePath" in data:
            self._input_object.loadImage(data["imagePath"])
            print(f"Image path updated: {data}")
        else:
            print(f"Unknown parameter change: {data}")

    def serialize(self):
        """
        Serializes the current state of the input device (Still Image Player) into a dictionary.
        """
        data = super().serialize()  # Call the base class method
        return data

    def deserialize(self, data):
        """
        Deserializes the input object from a dictionary and updates the graphical interface.
        """
        super().deserialize(data)
        self._name = data["name"]
        self.graphicInterface.deserialize(data)
