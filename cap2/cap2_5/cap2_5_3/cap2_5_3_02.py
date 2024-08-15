import numpy as np


# Creare tre matrici 2x2 per i canali R, G e B
R = np.array([[255, 0], [0, 255]])
G = np.array([[0, 255], [255, 0]])
B = np.array([[0, 0], [255, 255]])


# Impilare le tre matrici lungo il terzo asse per creare un'immagine RGB
RGB = np.dstack((R, G, B))
print("Image RGB:")
print(RGB)


# Dividere l'immagine RGB lungo il terzo asse per ottenere i canali R, G e B
R_split, G_split, B_split = np.dsplit(RGB, 3)
print("\nChannel R:")
print(R_split)
print("\nChannel G:")
print(G_split)
print("\nChannel B:")
print(B_split)