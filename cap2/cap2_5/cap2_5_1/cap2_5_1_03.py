import numpy as np

# crea un frame bianco con valori 255 su tutti i canali
whiteFrame = np.full((1080, 1920, 3), 255, dtype=np.uint8)

# usa matplotlib per mostrare l'immagine
import matplotlib.pyplot as plt

plt.imshow(whiteFrame)
plt.show()