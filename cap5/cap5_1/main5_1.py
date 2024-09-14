import atexit
import cProfile
import pstats
import sys

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from cap2.cap2_6.synchObject import SynchObject
from cap5.cap5_1.mainWindow5_1 import MainWindow5_1


def setPalette(_app):
    _app.setStyle("Fusion")
    darkPalette = QPalette()
    darkPalette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    darkPalette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    darkPalette.setColor(QPalette.ColorRole.Base, QColor(42, 42, 42))
    darkPalette.setColor(QPalette.ColorRole.AlternateBase, QColor(66, 66, 66))
    darkPalette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
    darkPalette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
    darkPalette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
    darkPalette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    darkPalette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
    darkPalette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
    darkPalette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    darkPalette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    darkPalette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
    darkPalette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, QColor(127, 127, 127))
    darkPalette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(127, 127, 127))
    darkPalette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(127, 127, 127))
    darkPalette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Highlight, QColor(80, 80, 80))
    darkPalette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.HighlightedText, QColor(127, 127, 127))

    _app.setPalette(darkPalette)


def run_app():
    synchObject = SynchObject()
    mainWin = MainWindow5_1(synchObject)
    mainWin.show()
    sys.exit(app.exec())


def print_profile_results(profiler):
    # Stampa i risultati del profiling
    stats = pstats.Stats(profiler).sort_stats('cumtime')
    stats.print_stats(20)  # Stampa i primi 20 risultati


if __name__ == "__main__":
    app = QApplication(sys.argv)
    setPalette(app)

    # Crea un profiler
    profiler = cProfile.Profile()

    # Registra la funzione che stamperà i risultati del profiler al termine del programma
    atexit.register(print_profile_results, profiler)

    # Avvia il profiler e la tua applicazione
    profiler.enable()
    run_app()
    profiler.disable()
