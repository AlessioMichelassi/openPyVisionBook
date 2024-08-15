import numpy as np
import matplotlib.pyplot as plt


# Creare una matrice rappresentante un'immagine RGB (ad esempio 4x4 pixel con 3 canali)
image = np.array([
   [[255, 0, 0], [255, 0, 0], [0, 255, 0], [0, 255, 0]],
   [[255, 0, 0], [255, 0, 0], [0, 255, 0], [0, 255, 0]],
   [[0, 0, 255], [0, 0, 255], [255, 255, 0], [255, 255, 0]],
   [[0, 0, 255], [0, 0, 255], [255, 255, 0], [255, 255, 0]]
], dtype=np.uint8)


# Dividere l'immagine in due parti uguali lungo l'asse verticale
top_half, bottom_half = np.vsplit(image, 2)


# Visualizzare le immagini divise
plt.subplot(1, 2, 1)
plt.imshow(top_half)
plt.title('Top Half')


plt.subplot(1, 2, 2)
plt.imshow(bottom_half)
plt.title('Bottom Half')


plt.show()
