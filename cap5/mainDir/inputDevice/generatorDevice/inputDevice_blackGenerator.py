from cap5.mainDir.inputDevice.baseDevice.inputDevice_Base import InputDevice
from cap5.mainDir.inputDevice.generatorDevice.inputObject.generator_Black import BlackGenerator


class InputDevice_BlackGenerator(InputDevice):
    """
    An InputDevice is any input of the mixer.
    It put together the thread, the input object and the graphic interface
    and act as interface to the mixer
    """

    def __init__(self, name, parent=None):
        super().__init__(name, parent)
        self._frame = None
        # set the input type and create the thread
        self.setInputObject(BlackGenerator())
        # set the graphic interface
        self.graphicInterface = None

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
        super().deserialize(data)  # Chiama il metodo della classe base
        # Eventuale logica aggiuntiva se è necessario reimpostare parametri specifici
        self._name = data["name"]
