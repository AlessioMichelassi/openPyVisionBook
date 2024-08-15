import numpy as np
import matplotlib.pyplot as plt


# Creazione di una griglia 8x8 con barre verticali
bar_height = 8
bar_width = 8


# Crea un array di indici di colonne
columns = np.arange(bar_width)


# Alterna tra colonne bianche (255) e nere (0)
bars = (columns % 2) * 255


# Replica le barre verticali su tutte le righe
bars = np.tile(bars, (bar_height, 1))


plt.imshow(bars, cmap='gray')
plt.title('Barre verticali')
plt.show()

