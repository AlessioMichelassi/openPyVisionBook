import cv2
import numpy as np
from skimage import exposure
import timeit
import matplotlib.pyplot as plt


# Funzione per applicare la correzione gamma usando LUT
def apply_gamma_lut(image, gamma):
    inv_gamma = 1.0 / gamma
    table = np.array([(i / 255.0) ** inv_gamma * 255 for i in range(256)]).astype(np.uint8)
    return cv2.LUT(image, table)


# Funzione per applicare la correzione gamma usando np.power
def apply_gamma_numpy(image, gamma):
    inv_gamma = 1.0 / gamma
    image = image / 255.0
    image = np.power(image, inv_gamma)
    return np.uint8(image * 255)


# Funzione per applicare la correzione gamma usando skimage
def apply_gamma_cv2(image, gamma):
    inv_gamma = 1.0 / gamma
    image = image / 255.0
    image = cv2.pow(image, inv_gamma)
    return np.uint8(image * 255)


# Crea un'immagine di test con quattro canali (incluso il canale alfa)
image = np.random.randint(0, 256, (1920, 1080, 4), dtype=np.uint8)

# Valore di gamma
gamma_value = 0.2

# Metodi per applicare la correzione gamma
methods = {
    'gamma_lut': apply_gamma_lut,
    'gamma_cv2': apply_gamma_cv2,
    'gamma_numpy': apply_gamma_numpy,
}

# Test delle prestazioni
for method_name, method in methods.items():
    time = timeit.timeit(lambda: method(image, gamma_value), number=1000)
    print(f"{method_name}: {time:.6f} seconds")

# Verifica che tutti i metodi producano lo stesso risultato
results = [method(image, gamma_value) for method_name, method in methods.items()]
for i in range(1, len(results)):
    if not np.array_equal(results[0], results[i]):
        print(f"Il metodo {list(methods.keys())[i]} produce un risultato diverso")

print("Verifica completata.")

# Visualizzazione delle immagini
fig, axes = plt.subplots(1, 4, figsize=(20, 10))

# Immagine originale
axes[0].imshow(cv2.cvtColor(image, cv2.COLOR_BGRA2RGBA))
axes[0].set_title('Original')

# Risultati dei metodi
for ax, (method_name, result) in zip(axes[1:], methods.items()):
    ax.imshow(cv2.cvtColor(results[list(methods.keys()).index(method_name)], cv2.COLOR_BGRA2RGBA))
    ax.set_title(method_name)

# Disattiva gli assi
for ax in axes:
    ax.axis('off')

plt.show()
