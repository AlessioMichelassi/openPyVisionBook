from cap5.cap5_3.videoHub.inputDevice.baseDevice.inputDevice_Base import InputDevice
from cap5.cap5_3.videoHub.inputDevice.generatorDevice.generatorWidget.noiseGeneratorWidget2 import NoiseGeneratorWidget2
from cap5.mainDir.inputs.generator.generator_Noise_Grain import GrainGenerator
from cap5.mainDir.inputs.generator.generator_Noise_Random import RandomNoiseGenerator
from cap5.mainDir.inputs.generator.generator_Noise_SaltAndPepper import SaltAndPepperGenerator


class InputDevice_NoiseGenerator(InputDevice):
    """
    An InputDevice is any input of the mixer.
    It put together the thread, the input object and the graphic interface
    and act as interface to the mixer
    """

    def __init__(self, name, parent=None):
        super().__init__(name, parent)
        isActive = False
        self._frame = None
        # Set the graphical interface
        self.graphicInterface = NoiseGeneratorWidget2()
        # Connect the parametersChanged signal from the widget to handle updates
        self.graphicInterface.typeChange.connect(self.onTypeChanged)
        self.graphicInterface.paramsChanged.connect(self.onParamsChanged)
        self.updateInputObject(self.currentNoiseType, self.currentParams)

    def updateInputObject(self, noiseType, params):
        print(f"Updating input object to noise type: {noiseType} with params: {params}")
        if self._thread and self._thread.isRunning():
            self.stop()
        # Creazione del nuovo inputObject
        inputObject = None
        if noiseType == "Random":
            inputObject = RandomNoiseGenerator()
        elif noiseType == "Salt and Pepper":
            inputObject = SaltAndPepperGenerator()
        elif noiseType == "Grain":
            inputObject = GrainGenerator()
        else:
            print(f"Unknown noise type: {noiseType}")
            return
        # Chiamiamo deserialize solo se ci sono parametri personalizzati
        if params:
            inputObject.deserialize(params)
        self.setInputObject(inputObject)
        if self.isActive:
            self.start()

    def onTypeChanged(self, data):
        noiseType = data.get('noiseType', 'Random')
        print(f"*** Noise Type Changed to {noiseType} ***")
        self.currentNoiseType = noiseType
        self.currentParams = {}  # Reset dei parametri
        self.updateInputObject(noiseType, self.currentParams)

    def onParamsChanged(self, data):
        # Escludi 'noiseType' dai parametri
        params = {k: v for k, v in data.items() if k != 'noiseType'}
        print(f"*** Noise Parameters Changed: {params} ***")
        self.currentParams.update(params)
        # Aggiorna i parametri dell'inputObject esistente
        self._input_object.deserialize(self.currentParams)

    def serialize(self):
        """
        Serializes the current state of the input device (Noise generator) into a dictionary.
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
