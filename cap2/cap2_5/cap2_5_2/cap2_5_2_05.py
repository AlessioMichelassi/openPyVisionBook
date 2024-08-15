import numpy as np
import matplotlib.pyplot as plt


x = np.arange(1920)
y = np.arange(1080)
X, Y = np.meshgrid(x, y)
Z = np.sin(np.sqrt(X**2 + Y**2) / 50)


plt.imshow(Z, cmap='gray')
plt.title('Pattern Circolare')
plt.show()
