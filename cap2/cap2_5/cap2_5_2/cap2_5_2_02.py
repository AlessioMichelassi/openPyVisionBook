from matplotlib import pyplot as plt
import numpy as np


colors = [
   (192, 192, 192),  # Grigio
   (192, 192, 0),    # Giallo
   (0, 192, 192),    # Ciano
   (0, 192, 0),      # Verde
   (192, 0, 192),    # Magenta
   (192, 0, 0),      # Rosso
   (0, 0, 192),      # Blu
   (0, 0, 0)         # Nero
]


width, height = 1920, 1080
# Crea una matrice vuota
bar_height = height
bar_width = width // len(colors)
bars = np.zeros((bar_height, width, 3), dtype=np.uint8)


# Riempie ogni sezione con il colore corrispondente
for i, color in enumerate(colors):
   bars[:, i * bar_width:(i + 1) * bar_width, :] = color


plt.imshow(bars)
plt.title('Barre colorate')


plt.show()
