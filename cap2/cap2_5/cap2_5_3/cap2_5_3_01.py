import numpy as np


A = np.ones((2, 2))
B = np.zeros((2, 2))


# Impilare verticalmente
vstack_result = np.vstack((A, B))
print("Vertical Stack Result:")
print(vstack_result)


# Impilare orizzontalmente
hstack_result = np.hstack((A, B))
print("Horizontal Stack Result:")
print(hstack_result)