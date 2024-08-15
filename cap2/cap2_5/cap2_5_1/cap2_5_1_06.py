import numpy as np
from matplotlib import pyplot as plt

# Gradienti orizzontali
gradient_v = np.linspace(0, 255, 1080, dtype=np.uint8)
gradient_v = np.tile(gradient_v, (1920, 1)).T


plt.imshow(gradient_v, cmap='gray')
plt.title('Gradient Orizzontale')
plt.show()
