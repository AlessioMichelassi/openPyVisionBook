import numpy as np
import matplotlib.pyplot as plt


# Creare una mappa di intensità logaritmica
log_space = np.logspace(0, 2, 1920, dtype=np.float32)
log_space = np.tile(log_space, (1080, 1))


plt.imshow(log_space, cmap='gray', norm=plt.Normalize(vmin=log_space.min(), vmax=log_space.max()))
plt.title('Pattern Logaritmico')
plt.show()
