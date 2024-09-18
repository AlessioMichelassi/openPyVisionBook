import json
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *

from cap5.mainDir.outputDevice.commonWidgets.sliderPlus import SliderTextWidget


class CodecWidget(QWidget):
    btnLoad: QPushButton
    btnSave: QPushButton
    cmbUserPreset: QComboBox
    cmbCodec: QComboBox
    cmbProfile: QComboBox
    cmbPixelFormat: QComboBox
    cmbPreset: QComboBox
    cmbRateControl: QComboBox
    cmbTune: QComboBox
    sliderBitrate: SliderTextWidget
    sliderBufferSize: SliderTextWidget
    sliderKeyframeInterval: SliderTextWidget
    lblCodec: QLabel
    lblProfile: QLabel
    lblPixelFormat: QLabel
    lblPreset: QLabel
    lblRateControl: QLabel
    lblTune: QLabel

    presetDictionary = {}

    def __init__(self, codec_permutation, parent=None):
        super(CodecWidget, self).__init__(parent)
        self.codec_permutation = codec_permutation
        self.initWidgets()
        self.initUI()
        self.initConnections()
        self.updateProfileOptions()

    def initWidgets(self):
        # Bitrate and Buffer Size Sliders
        self.sliderBitrate = SliderTextWidget("Bitrate", min_value=500, max_value=10000, initial_value=4500)
        self.sliderBufferSize = SliderTextWidget("Buffer Size", min_value=1000, max_value=30000, initial_value=6000)
        # Keyframe Interval (GOP) Slider
        self.sliderKeyframeInterval = SliderTextWidget("Keyframe Interval (GOP)", min_value=0, max_value=200,
                                                       initial_value=2)

        # Initialize Buttons and User Preset ComboBox
        self.btnLoad = QPushButton("Load Profile")
        self.btnSave = QPushButton("Save Profile")
        self.cmbUserPreset = QComboBox(self)

        # Codec, Profile, Pixel Format, Preset ComboBoxes
        self.lblCodec = QLabel("Select Codec:")
        self.cmbCodec = QComboBox(self)
        self.cmbCodec.addItems(self.codec_permutation.keys())

        self.lblProfile = QLabel("Profile:")
        self.cmbProfile = QComboBox(self)

        self.lblPixelFormat = QLabel("Pixel Format:")
        self.cmbPixelFormat = QComboBox(self)

        self.lblPreset = QLabel("Preset:")
        self.cmbPreset = QComboBox(self)

        # Rate Control ComboBox
        self.lblRateControl = QLabel("Rate Control:")
        self.cmbRateControl = QComboBox(self)
        self.cmbRateControl.addItems(["CBR", "VBR", "ABR"])

        # Tune ComboBox
        self.lblTune = QLabel("Tune:")
        self.cmbTune = QComboBox(self)
        self.cmbTune.addItems(["None", "film", "animation", "grain", "stillimage", "fastdecode", "zerolatency"])

    @staticmethod
    def return2ColumnLayout(label1, widget1, label2, widget2):
        layout = QHBoxLayout()
        first_column = QVBoxLayout()
        first_column.addWidget(label1)
        first_column.addWidget(widget1)

        second_column = QVBoxLayout()
        second_column.addWidget(label2)
        second_column.addWidget(widget2)

        layout.addLayout(first_column)
        layout.addLayout(second_column)

        return layout

    def initUI(self):
        main_layout = QVBoxLayout()

        # Add Load, Save Buttons and User Preset ComboBox
        user_preset_layout = QHBoxLayout()
        user_preset_layout.addWidget(self.cmbUserPreset)
        user_preset_layout.addWidget(self.btnLoad)
        user_preset_layout.addWidget(self.btnSave)
        main_layout.addLayout(user_preset_layout)

        # Codec, Profile, Pixel Format Layouts
        codec_layout = self.return2ColumnLayout(self.lblCodec, self.cmbCodec, self.lblProfile, self.cmbProfile)
        pixel_format_layout = self.return2ColumnLayout(self.lblPixelFormat, self.cmbPixelFormat,
                                                       self.lblPreset, self.cmbPreset)
        tune_layout = self.return2ColumnLayout(self.lblRateControl, self.cmbRateControl,
                                               self.lblTune, self.cmbTune)

        main_layout.addLayout(codec_layout)
        main_layout.addLayout(pixel_format_layout)
        main_layout.addLayout(tune_layout)

        # Add Bitrate and Buffer Size Sliders
        main_layout.addWidget(self.sliderBitrate)
        main_layout.addWidget(self.sliderBufferSize)

        # Add Keyframe Interval Slider
        main_layout.addWidget(self.sliderKeyframeInterval)

        self.setLayout(main_layout)

    def initConnections(self):
        # Update profiles and presets when codec or profile is changed
        self.cmbCodec.currentTextChanged.connect(self.updateProfileOptions)
        self.cmbProfile.currentTextChanged.connect(self.updatePixelFormatAndPreset)
        self.btnLoad.clicked.connect(self.loadProfile)
        self.btnSave.clicked.connect(self.saveProfile)
        self.cmbUserPreset.currentIndexChanged.connect(self.updatePreset)

    def updateProfileOptions(self):
        codec = self.cmbCodec.currentText()
        profiles = self.codec_permutation[codec]['profiles']

        self.cmbProfile.clear()
        self.cmbProfile.addItems(profiles)
        self.cmbProfile.setCurrentIndex(4)
        self.updatePixelFormatAndPreset()

    def updatePixelFormatAndPreset(self):
        codec = self.cmbCodec.currentText()
        profile = self.cmbProfile.currentText()

        # Update Pixel Formats
        pixel_formats = self.codec_permutation[codec]['pixelFormats'].get(profile, [])
        self.cmbPixelFormat.clear()
        self.cmbPixelFormat.addItems(pixel_formats)

        # Update Presets
        presets = self.codec_permutation[codec]['presets'].get(profile, [])
        self.cmbPreset.clear()
        self.cmbPreset.addItems(presets)

    def openPresetsFile(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        dialog.setNameFilter("JSON Files (*.json)")
        dialog.setViewMode(QFileDialog.ViewMode.List)
        dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
        dialog.setDirectory(".")
        if dialog.exec():
            self.openPreset(dialog.selectedFiles()[0])

    def openPreset(self, presetFile):
        with open(presetFile, "r") as f:
            json_data = json.load(f)
            self.deserialize(json_data)
            if self.cmbUserPreset.findText(presetFile) == -1:
                self.cmbUserPreset.addItem(presetFile)

    def saveProfile(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.FileMode.AnyFile)
        dialog.setNameFilter("JSON Files (*.json)")
        dialog.setViewMode(QFileDialog.ViewMode.List)
        dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        dialog.setDirectory(".")
        if dialog.exec():
            self.savePreset(dialog.selectedFiles()[0])

    def savePreset(self, presetFile):
        with open(presetFile, "w") as f:
            json.dump(self.serialize(), f)
            if self.cmbUserPreset.findText(presetFile) == -1:
                self.cmbUserPreset.addItem(presetFile)

    def loadProfile(self):
        self.openPresetsFile()

    def updatePreset(self):
        preset = self.cmbPreset.currentText()
        if preset == "User":
            self.loadProfile()
        else:
            self.cmbUserPreset.setCurrentText(preset)
            self.openPreset(preset)

    def serialize(self):
        return {
            "codec": self.cmbCodec.currentText(),
            "profile": self.cmbProfile.currentText(),
            "pixelFormat": self.cmbPixelFormat.currentText(),
            "preset": self.cmbPreset.currentText(),
            "rateControl": self.cmbRateControl.currentText(),
            "bitrate": self.sliderBitrate.getValue(),
            "bufferSize": self.sliderBufferSize.getValue(),
            "tune": self.cmbTune.currentText(),
            "keyframeInterval": self.sliderKeyframeInterval.getValue()
        }

    def deserialize(self, data):
        self.cmbCodec.setCurrentText(data.get("codec", "libx264"))
        self.cmbProfile.setCurrentText(data.get("profile", "baseline"))
        self.cmbPixelFormat.setCurrentText(data.get("pixelFormat", "yuv420p"))
        self.cmbPreset.setCurrentText(data.get("preset", "ultrafast"))
        self.cmbRateControl.setCurrentText(data.get("rateControl", "CBR"))
        self.sliderBitrate.setValue(data.get("bitrate", 2500))
        self.sliderBufferSize.setValue(data.get("bufferSize", 10000))
        self.cmbTune.setCurrentText(data.get("tune", "None"))
        self.sliderKeyframeInterval.setValue(data.get("keyframeInterval", 2))


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication

    codecPermutation = {
        'libx264': {
            'profiles': ['baseline', 'main', 'high', 'high10', 'high422', 'high444'],
            'pixelFormats': {
                'baseline': ['yuv420p'],
                'main': ['yuv420p'],
                'high': ['yuv420p'],
                'high10': ['yuv422p10le', 'yuv420p10le'],
                'high422': ['yuv422p'],
                'high444': ['yuv444p']
            },
            'presets': {
                'baseline': ['ultrafast', 'superfast', 'veryfast', 'fast', 'medium', 'slow', 'slower', 'veryslow'],
                'main': ['ultrafast', 'superfast', 'veryfast', 'fast', 'medium', 'slow', 'slower', 'veryslow'],
                'high': ['ultrafast', 'superfast', 'veryfast', 'fast', 'medium', 'slow', 'slower', 'veryslow'],
                'high10': ['ultrafast', 'superfast', 'veryfast', 'fast', 'medium', 'slow', 'slower', 'veryslow'],
                'high422': ['ultrafast', 'superfast', 'veryfast', 'fast', 'medium', 'slow', 'slower', 'veryslow'],
                'high444': ['ultrafast', 'superfast', 'veryfast', 'fast', 'medium', 'slow', 'slower', 'veryslow']
            }
        },
        'libx265': {
            'profiles': ['main', 'main10', 'main422-10', 'main444-10'],
            'pixelFormats': {
                'main': ['yuv420p'],
                'main10': ['yuv420p10le', 'yuv422p10le'],
                'main422-10': ['yuv422p10le'],
                'main444-10': ['yuv444p10le']
            },
            'presets': {
                'main': ['ultrafast', 'superfast', 'veryfast', 'fast', 'medium', 'slow', 'slower', 'veryslow'],
                'main10': ['ultrafast', 'superfast', 'veryfast', 'fast', 'medium', 'slow', 'slower', 'veryslow'],
                'main422-10': ['ultrafast', 'superfast', 'veryfast', 'fast', 'medium', 'slow', 'slower', 'veryslow'],
                'main444-10': ['ultrafast', 'superfast', 'veryfast', 'fast', 'medium', 'slow', 'slower', 'veryslow']
            }
        }
    }

    app = QApplication([])
    window = CodecWidget(codecPermutation)
    window.show()
    app.exec()
