import atexit
import cProfile
import ctypes
import io
import pstats
import sys

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
import threading

from mainWindow import MainWindow

# Define constants for colors
WINDOW_COLOR = QColor(53, 53, 53)
TEXT_COLOR = Qt.GlobalColor.white
BASE_COLOR = QColor(42, 42, 42)
ALTERNATE_BASE_COLOR = QColor(66, 66, 66)
BRIGHT_TEXT_COLOR = Qt.GlobalColor.red
LINK_COLOR = QColor(42, 130, 218)
DISABLED_TEXT_COLOR = QColor(127, 127, 127)
DISABLED_HIGHLIGHT_COLOR = QColor(80, 80, 80)


def set_color(palette, role, color):
    palette.setColor(role, color)


def setPalette(app):
    app.setStyle("Fusion")
    dark_palette = QPalette()
    # Normal state colors
    set_color(dark_palette, QPalette.ColorRole.Window, WINDOW_COLOR)
    set_color(dark_palette, QPalette.ColorRole.WindowText, TEXT_COLOR)
    set_color(dark_palette, QPalette.ColorRole.Base, BASE_COLOR)
    set_color(dark_palette, QPalette.ColorRole.AlternateBase, ALTERNATE_BASE_COLOR)
    set_color(dark_palette, QPalette.ColorRole.ToolTipBase, TEXT_COLOR)
    set_color(dark_palette, QPalette.ColorRole.ToolTipText, TEXT_COLOR)
    set_color(dark_palette, QPalette.ColorRole.Text, TEXT_COLOR)
    set_color(dark_palette, QPalette.ColorRole.Button, WINDOW_COLOR)
    set_color(dark_palette, QPalette.ColorRole.ButtonText, TEXT_COLOR)
    set_color(dark_palette, QPalette.ColorRole.BrightText, BRIGHT_TEXT_COLOR)
    set_color(dark_palette, QPalette.ColorRole.Link, LINK_COLOR)
    set_color(dark_palette, QPalette.ColorRole.Highlight, LINK_COLOR)
    set_color(dark_palette, QPalette.ColorRole.HighlightedText, TEXT_COLOR)

    # Disabled state colors
    dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, DISABLED_TEXT_COLOR)
    dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, DISABLED_TEXT_COLOR)
    dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, DISABLED_TEXT_COLOR)
    dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Highlight, DISABLED_HIGHLIGHT_COLOR)
    dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.HighlightedText, DISABLED_TEXT_COLOR)

    app.setPalette(dark_palette)


def set_dpi_awareness():
    try:
        # Imposta la consapevolezza DPI a livello di sistema
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception as e:
        print(f"Errore nell'impostare la DPI awareness: {e}")



def main():
    def clean_up():
        # Assicurati di fermare tutti i thread e timer qui
        print("Eseguendo la pulizia prima di uscire.")
        app.quit()  # Chiude l'applicazione Qt
    # Prima di creare l'applicazione, imposta l'attributo DPI
    set_dpi_awareness()
    app = QApplication(sys.argv)
    setPalette(app)

    mainWin = MainWindow()
    mainWin.show()

    # Connessione dei segnali
    mainWin.new_SIGNAL.connect(lambda: handle_new_project(mainWin))
    mainWin.newAndLoad_SIGNAL.connect(lambda: handle_load_project(mainWin))
    app.aboutToQuit.connect(clean_up)
    sys.exit(app.exec())


def handle_new_project(mainWin):
    """Gestisce la creazione di un nuovo progetto"""
    mainWin.close()
    mainWin = MainWindow()
    mainWin.show()


def handle_load_project(mainWin, data):
    """Gestisce il caricamento di un progetto"""
    # Logica per il caricamento di un progetto
    mainWin.close()
    mainWin = MainWindow()
    mainWin.deserialize(data)
    mainWin.show()


if __name__ == "__main__":
    pr = cProfile.Profile()
    pr.enable()


    def exit_handler():
        print("Thread attivi alla chiusura:", threading.enumerate())
        pr.disable()
        s = io.StringIO()
        sortby = 'cumulative'
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats(26)
        print(s.getvalue())


    atexit.register(exit_handler)
    main()
