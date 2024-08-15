# Creazione della matrice 8x8 bianca
import numpy as np
from matplotlib import pyplot as plt

whiteMat = np.ones((8, 8), dtype=np.uint8) * 255


# Creazione della matrice 8x8 nera
blackMat = np.zeros((8, 8), dtype=np.uint8)


# Creazione di un'immagine vuota 8x8 (per contenere metà dell'una e metà dell'altra)
combinedMat = np.zeros((8, 8), dtype=np.uint8)


# Combinazione delle due matrici
combinedMat[:, :4] = whiteMat[:, :4]
combinedMat[:, 4:] = blackMat[:, 4:]


# Visualizzazione dell'immagine combinata
plt.imshow(combinedMat, cmap='gray')
plt.title('Metà Bianco e Metà Nero')


plt.show()
