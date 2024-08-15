import numpy as np

# crea un frame di 1 su tutti i canali poi moltiplicato per 255
# per ottenere un frame bianco
oneFrame = np.ones((1080, 1920, 3), dtype=np.uint8) * 255

# usa matplotlib per mostrare l'immagine
import matplotlib.pyplot as plt

plt.imshow(oneFrame)
plt.show()