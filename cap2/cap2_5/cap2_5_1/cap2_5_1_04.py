import numpy as np

# crea un frame nero con valori random su tutti i canali
randomFrame = np.random.randint(0, 256, (1080, 1920, 3), dtype=np.uint8)

# usa matplotlib per mostrare l'immagine
import matplotlib.pyplot as plt

plt.imshow(randomFrame)
plt.show()