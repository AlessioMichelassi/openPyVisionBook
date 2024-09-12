import sys
import tracemalloc
import matplotlib.pyplot as plt
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication

from cap5.cap5_1.mainWindow5_1 import MainWindow5_1
from mainX import MainWindowX
from cap5.cap5_2.mainX2 import MainWindowX2
from cap5.mainDir.inputs.synchObject import SynchObject

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
fps_value_new_method2 = measure_fps_over_time(MainWindow5_1)
# Statistiche sull'uso della memoria
current, peak = tracemalloc.get_traced_memory()
print(f"Uso di memoria corrente: {current / 10 ** 6}MB; Picco: {peak / 10 ** 6}MB")
fps_value_new_method3 = measure_fps_over_time(MainWindowX)
# Statistiche sull'uso della memoria
current, peak = tracemalloc.get_traced_memory()
print(f"Uso di memoria corrente: {current / 10 ** 6}MB; Picco: {peak / 10 ** 6}MB")
fps_value_new_method4 = measure_fps_over_time(MainWindowX2)
# Statistiche sull'uso della memoria
current, peak = tracemalloc.get_traced_memory()
print(f"Uso di memoria corrente: {current / 10 ** 6}MB; Picco: {peak / 10 ** 6}MB")
#fps_values_old_method = measure_fps_over_time(MainWindow5_1)


# Calcola la media degli FPS
#average_fps_old = sum(fps_values_old_method) / len(fps_values_old_method)
average_fps_new2 = sum(fps_value_new_method2) / len(fps_value_new_method2)
average_fps_new3 = sum(fps_value_new_method3) / len(fps_value_new_method3)
average_fps_new4 = sum(fps_value_new_method4) / len(fps_value_new_method4)

#print(f"Old Method - Average FPS: {average_fps_old:.2f}")
print(f"main - Average FPS: {average_fps_new2:.2f}")
print(f"main2 - Average FPS: {average_fps_new3:.2f}")
print(f"main3 - Average FPS: {average_fps_new4:.2f}")

# Traccia un grafico per confrontare
#plt.plot(fps_values_old_method, label="Old Method")
plt.plot(fps_value_new_method2, label="mainX")
plt.plot(fps_value_new_method3, label="mainX 2")
plt.plot(fps_value_new_method4, label="mainX 3")
plt.xlabel("Time (seconds)")
plt.ylabel("FPS")
plt.title("FPS Over Time - Old vs New Method")
plt.legend()
plt.show()
