import numpy as np
import matplotlib.pyplot as plt
arr = np.arange(0, 1920, dtype=np.uint8)
arr = np.tile(arr, (1080, 1))
print(arr)
print(arr.shape)
print(arr.dtype)
print(arr.min(), arr.max())


plt.imshow(arr, cmap='gray')
plt.show()
