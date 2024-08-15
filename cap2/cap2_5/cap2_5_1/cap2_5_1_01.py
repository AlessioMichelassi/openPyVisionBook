import numpy as np

# crea un frame nero con valori 0 su tutti i canali
blackFrame = np.zeros((1080, 1920, 3), dtype=np.uint8)

# usa matplotlib per mostrare l'immagine
import matplotlib.pyplot as plt

plt.imshow(blackFrame)
plt.show()