import sys

import tracemalloc
import matplotlib.pyplot as plt
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

from cap5.cap5_1.mainWindow5_1 import MainWindow5_1
from cap5.cap5_2.mainX2 import MainWindowX2
from cap5.mainDir.inputs.synchObject import SynchObject
from mainX import MainWindowX
from mainX3 import MainWindowX3

tracemalloc.start()


def measure_fps_over_time(MainWindowClass, duration=60, interval=1):
    # Crea un contesto di QApplication per questa esecuzione
    app = QApplication(sys.argv)
    synchObject = SynchObject()
    mw = MainWindowClass(synchObject)
    mw.show()

    fps_values = []
    memoryallocation = []

    def collect_fps():
        current_fps = mw.mixBus.last_fps
        fps_values.append(current_fps)

    # Imposta un timer per raccogliere gli FPS ogni 'interval' secondi
    timer = QTimer()
    timer.timeout.connect(collect_fps)
    timer.start(interval * 1000)  # Converte l'intervallo da secondi a millisecondi

    # Ferma la misurazione dopo 'duration' secondi
    QTimer.singleShot(duration * 1000, app.quit)

    # Avvia l'applicazione
    app.exec()

    return fps_values


# Esegui per ciascuna versione del sistema
fps_value_new_method2 = measure_fps_over_time(MainWindowX3)
current, peak = tracemalloc.get_traced_memory()
print(f"Uso di memoria corrente: {current / 10 ** 6}MB; Picco: {peak / 10 ** 6}MB")

average_fps_new2 = sum(fps_value_new_method2) / len(fps_value_new_method2)
print(f"FPS medi: {average_fps_new2:.2f}")

plt.plot(fps_value_new_method2, label="mainX")
# disegna una linea orizzontale per la media
plt.axhline(y=average_fps_new2, color="r", linestyle="--", label=f"Media: {average_fps_new2:.2f}")
plt.xlabel("Tempo (s)")
plt.ylabel("FPS")
plt.legend()

plt.show()
