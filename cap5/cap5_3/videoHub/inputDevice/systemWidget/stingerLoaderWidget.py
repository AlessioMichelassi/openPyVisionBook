import json
import logging
import os

import cv2
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *

from mainDir.inputs.player.player_StingerMixBus import StingerForMixBusPlayer
from mainDir.videoHub.systemWidget.threadLoader.asyncCacheLoader import AsyncCacheLoader
from mainDir.videoHub.systemWidget.threadLoader.cacheWorker import CacheWorker
from mainDir.videoHub.systemWidget.threadLoader.progressDisplay import ProgressDisplay
from mainDir.videoHub.systemWidget.threadLoader.stingerLoaderV04T import StingerLoaderV04T


class StingerLoaderWidget(QWidget):
    stingerReady = pyqtSignal(QObject)
    isCached = False

    def __init__(self, name="StingerLoader1", parent=None):
        super().__init__(parent)
        self.type = "StingerLoader"
        self.name = name
        self.cacheDirectory = None
        self.stingerNumber = 1
        self.inputObject = None
        self.loader = None
        self.cacheWorker = None
        self.progressDisplay = None
        self.cacheLoader = None

        # UI Elements
        self.btnLoadNewStinger = QPushButton("Load New Stinger", self)
        self.btnLoadCachedStinger = QPushButton("Load Cached Stinger", self)
        self.lneImagePath = QLineEdit("", self)
        self.btnCache = QPushButton("Save to Cache", self)
        self.btnCache.setEnabled(False)

        self.initUI()
        self.initConnections()

    def initUI(self):
        layout = QHBoxLayout(self)
        layout.addWidget(self.lneImagePath)
        layout.addWidget(self.btnLoadNewStinger)
        layout.addWidget(self.btnLoadCachedStinger)
        layout.addWidget(self.btnCache)
        self.setLayout(layout)

    def initConnections(self):
        self.btnLoadNewStinger.clicked.connect(self.onLoadDirectory)
        self.btnLoadCachedStinger.clicked.connect(self.onLoadCachedStinger)
        self.btnCache.clicked.connect(self.onBtnCache)

    def getName(self):
        return self.name

    def setName(self, name):
        self.name = name

    def onLoadDirectory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Stinger Directory")
        if directory:
            self.lneImagePath.setText(directory)
            self.startImageProcessing(directory)

    def startImageProcessing(self, directory):
        logging.info(f"Processing directory: {directory}")

        if not os.path.isdir(directory):
            logging.error(f"Error: Directory does not exist: {directory}")
            return

        if self.loader:
            self.loader.stop()
            self.loader.wait()

        self.loader = StingerLoaderV04T(directory)
        self.progressDisplay = ProgressDisplay(self.loader, title="Loading Stinger", message="Loading Stinger...")
        self.progressDisplay.show()

        self.loader.stingerReady.connect(self.onStingerReady)
        self.loader.start()

    def onStingerReady(self):
        self.inputObject = StingerForMixBusPlayer(self.loader.path, self.stingerNumber)
        self.inputObject.setStingerPremultipliedImages(self.loader.stingerPreMultipliedImages)
        self.inputObject.setStingerInvAlphaImages(self.loader.stingerInvAlphaImages)

        self.btnCache.setEnabled(True)
        self.stingerReady.emit(self.inputObject)

    def onBtnCache(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Cache Directory")
        if directory:
            self.cacheDirectory = directory

            if self.cacheWorker:
                self.cacheWorker.stop()
                self.cacheWorker.wait()

            self.cacheWorker = CacheWorker(self.saveToCache)
            self.progressDisplay = ProgressDisplay(self.cacheWorker, title="Saving Cache", message="Saving to Cache...")
            self.progressDisplay.show()
            self.cacheWorker.start()

    def saveToCache(self, progress_callback=None):
        if not self.inputObject:
            return

        name = os.path.basename(self.lneImagePath.text())
        premultiply_directory = os.path.join(self.cacheDirectory, f"{name}_premultiply")
        inv_alpha_directory = os.path.join(self.cacheDirectory, f"{name}_invAlpha")

        os.makedirs(premultiply_directory, exist_ok=True)
        os.makedirs(inv_alpha_directory, exist_ok=True)

        total_images = len(self.inputObject.stingerPreMultipliedImages)
        for i, img in enumerate(self.inputObject.stingerPreMultipliedImages):
            cv2.imwrite(os.path.join(premultiply_directory, f"frame_{i:03d}.png"), img)
            if progress_callback:
                progress_callback.emit(int((i + 1) / total_images * 50))  # 50% per il salvataggio premultiplied

        for i, img in enumerate(self.inputObject.stingerInvAlphaImages):
            cv2.imwrite(os.path.join(inv_alpha_directory, f"frame_{i:03d}.png"), img)
            if progress_callback:
                progress_callback.emit(50 + int((i + 1) / total_images * 50))  # 50% successivo per invAlpha

        # Salva il file JSON con i percorsi delle cache
        cache_data = {
            'stingerFolder': self.lneImagePath.text(),
            'premultiplyDirectory': premultiply_directory,
            'invAlphaDirectory': inv_alpha_directory
        }
        with open(os.path.join(self.cacheDirectory, f"{name}.cachedStinger.json"), 'w') as f:
            json.dump(cache_data, f, indent=4)

        logging.info("Cache saved successfully.")

    def onLoadCachedStinger(self):
        cache_file_path, _ = QFileDialog.getOpenFileName(self, "Open Cached Stinger JSON", "", "JSON Files (*.json)")
        if cache_file_path:
            with open(cache_file_path, 'r') as f:
                cache_data = json.load(f)

            stinger_folder = cache_data.get('stingerFolder')
            premultiply_directory = cache_data.get('premultiplyDirectory')
            inv_alpha_directory = cache_data.get('invAlphaDirectory')
            self.lneImagePath.setText(stinger_folder)
            logging.info(f"Stinger Folder: {stinger_folder}")
            logging.info(f"Premultiply Directory: {premultiply_directory}")
            logging.info(f"Inv Alpha Directory: {inv_alpha_directory}")

            if not os.path.isdir(stinger_folder):
                logging.error(f"Error: Stinger folder does not exist: {stinger_folder}")
                return

            if not os.path.isdir(premultiply_directory):
                logging.error(f"Error: Premultiply directory does not exist: {premultiply_directory}")
                return

            if not os.path.isdir(inv_alpha_directory):
                logging.error(f"Error: Inv Alpha directory does not exist: {inv_alpha_directory}")
                return

            self.startLoadingCachedImages(premultiply_directory, inv_alpha_directory)

    def startLoadingCachedImages(self, premultiply_directory, inv_alpha_directory):
        if self.cacheLoader:
            self.cacheLoader.stop()
            self.cacheLoader.wait()

        self.cacheLoader = AsyncCacheLoader(premultiply_directory, inv_alpha_directory)
        self.progressDisplay = ProgressDisplay(self.cacheLoader, title="Loading Cached Images",
                                               message="Loading Cache...")
        self.progressDisplay.show()

        self.cacheLoader.imagesLoaded.connect(self.onCachedImagesLoaded)
        self.cacheLoader.operationCompleted.connect(self.progressDisplay.onOperationCompleted)
        self.cacheLoader.start()

    def onCachedImagesLoaded(self, premultiplied_images, inv_alpha_images):
        self.inputObject = StingerForMixBusPlayer(self.lneImagePath.text(), self.stingerNumber)
        self.inputObject.setStingerPremultipliedImages(premultiplied_images)
        self.inputObject.setStingerInvAlphaImages(inv_alpha_images)

        self.btnCache.setEnabled(True)
        self.stingerReady.emit(self.inputObject)

    def closeEvent(self, event, _QCloseEvent=None):
        if self.loader:
            self.loader.stop()
            self.loader.wait()

        if self.cacheWorker:
            self.cacheWorker.stop()
            self.cacheWorker.wait()

        super().closeEvent(event)

    def serialize(self):
        return {
            'name': self.getName(),
            'type': self.type,
            'imagePath': self.lneImagePath.text(),
            'inputObject': self.inputObject.serialize() if self.inputObject else None
        }

    def deserialize(self, data):
        self.setName(data['name'])
        self.lneImagePath.setText(data['imagePath'])
        if data['inputObject']:
            self.inputObject = StingerForMixBusPlayer(data['imagePath'], self.stingerNumber)
            self.inputObject.deserialize(data['inputObject'])
            self.stingerReady.emit(self.inputObject)
