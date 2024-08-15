import numpy as np
from matplotlib import pyplot as plt

# Gradienti orizzontali
gradient_h = np.linspace(0, 255, 1920, dtype=np.uint8)
gradient_h = np.tile(gradient_h, (1080, 1))


plt.imshow(gradient_h, cmap='gray')
plt.title('Gradient Orizzontale')
plt.show()
