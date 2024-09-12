import json
import os

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QApplication

from cap5.mainDir.inputs.stillImageLoader import StillImageLoader
from cap5.mainDir.mixBus.stingerInputLoader_03_thread import StingerLoaderThread03, StingerDisplay


class DataManager(QObject):
    stingerObject = None
    stillObject = None
    loaderThread = None
    stingerDisplay = None
    errorSignal = pyqtSignal(str)
    statusSignal = pyqtSignal(str)
    readySignal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.stingerPath = ""
        self.stillImagePath = ""

        # Variabili di stato
        self.isReady = False
        self.isLoading = False
        self.hasError = False
        currentDir = os.path.dirname(os.path.realpath(__file__))
        self.currentFile = os.path.join(currentDir, "data.json")

    def loadData(self):
        """
        This function loads the data from the data.json file.
        If not found the file or if the file is corrupted, it creates a new one.
        and emit an Error signal.
        :return:
        """
        print("Loading data")
        self.isLoading = True
        self.hasError = False
        self.statusSignal.emit("Loading data")

        if not os.path.exists(self.currentFile):
            self.saveData()
        try:
            with open(self.currentFile, "r") as f:
                data = json.load(f)
                self.stingerPath = data.get("stingerPath", "")
                self.getStingerObject()
                self.stillImagePath = data.get("stillImagePath", "")
                self.getStillObject()
                self.checkReadyState()
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"There was an error loading the data: {e}")
            self.hasError = True
            self.isReady = False
            self.errorSignal.emit("Error loading data")
        finally:
            self.isLoading = False
            self.statusSignal.emit("Data loaded")

    def saveData(self):
        """
        This function saves the data to the data.json file.
        :param data: dictionary with the data to save
        :return:
        """
        self.isLoading = True
        self.statusSignal.emit("Saving data")

        try:
            with open(self.currentFile, "w") as f:
                json.dump(self.serialize(), f)
        except IOError as e:
            print(f"Error saving data: {e}")
            self.hasError = True
            self.errorSignal.emit("Error saving data")
        finally:
            self.isLoading = False
            self.statusSignal.emit("Data saved")

    def setStingerPath(self, path):
        """
        This function sets the stinger path and loads the stinger object.
        :param path: path to the stinger folder
        :return:
        """
        self.stingerPath = path
        if os.path.exists(self.stingerPath):
            self.getStingerObject()
        else:
            self.hasError = True
            self.errorSignal.emit("Stinger path not found")
        self.saveData()

    def getStingerObject(self):
        """
        This function creates the stinger object and the stinger display object.
        :return:
        """
        self.isLoading = True
        self.statusSignal.emit("Loading stinger")

        self.loaderThread = StingerLoaderThread03(self.stingerPath)
        self.stingerDisplay = StingerDisplay(self.loaderThread)
        self.loaderThread.stingerReady.connect(self.onStingerReady)
        self.loaderThread.start()
        self.stingerDisplay.show()

    def onStingerReady(self):
        """
        This function is called when the stinger is loaded.
        :return:
        """
        self.stingerObject = self.loaderThread
        self.isLoading = False
        self.stingerDisplay.close()
        self.statusSignal.emit("Stinger ready")
        self.checkReadyState()

    def setStillImagePath(self, path):
        """
        This function sets the still image path and loads the still object.
        :param path:  path to the still image
        :return:
        """
        self.stillImagePath = path
        if os.path.exists(self.stillImagePath):
            self.getStillObject()
        else:
            self.hasError = True
            self.errorSignal.emit("Still image path not found")
        self.saveData()

    def getStillObject(self):
        self.stillObject = StillImageLoader(self.stillImagePath, None)
        self.statusSignal.emit("Still image ready")
        self.checkReadyState()

    def checkReadyState(self):
        """
        This function checks if both the stinger and still image are ready.
        If both are ready, it emits the ready signal.
        """
        if self.stingerObject and self.stillObject:
            self.isReady = True
            self.readySignal.emit()

    def serialize(self):
        return {
            "stingerPath": self.stingerPath,
            "stillImagePath": self.stillImagePath,
        }


if __name__ == "__main__":
    app = QApplication([])
    dataManager = DataManager()

    def print_status(status):
        print(f"Status: {status}")

    def print_ready():
        print("All assets are ready!")

    dataManager.errorSignal.connect(print)
    dataManager.statusSignal.connect(print_status)
    dataManager.readySignal.connect(print_ready)

    dataManager.loadData()
    print(dataManager.stingerPath)
    print(dataManager.stillImagePath)
    dataManager.setStingerPath(r"C:\pythonCode\openPyVisionBook\openPyVisionBook\cap5\mainDir\inputs\stingerDefault")
    dataManager.setStillImagePath(r"C:\pythonCode\openPyVisionBook\openPyVisionBook\cap5\mainDir\inputs\stillDefault"
                                  r"\Grass_Valley_110_Switcher.jpg")
    dataManager.saveData()
    print(dataManager.serialize())
    print("Data saved and loaded successfully")

    app.exec()
