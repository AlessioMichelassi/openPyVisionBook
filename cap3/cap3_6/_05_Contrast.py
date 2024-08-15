import timeit

import cv2
import numpy as np
import matplotlib.pyplot as plt


def compute_local_contrast(image, window_size=3):
    """
    Calcola il contrasto locale usando il metodo di Peli.
    """
    # Converti l'immagine in scala di grigi
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY).astype(np.float32)

    # Calcola la luminanza media locale usando un filtro a media mobile
    kernel = np.ones((window_size, window_size), np.float32) / (window_size ** 2)
    local_mean = cv2.filter2D(gray_image, -1, kernel)

    # Calcola il contrasto locale
    local_contrast = (gray_image - local_mean) / (gray_image + local_mean + 1e-6)

    return local_contrast


def enhance_contrast(image, contrast_factor=1.5):
    """
    Migliora il contrasto dell'immagine applicando il contrasto locale calcolato.
    """
    # Calcola il contrasto locale
    local_contrast = compute_local_contrast(image)

    # Moltiplica il contrasto locale per un fattore di miglioramento
    enhanced_image = image.astype(np.float32) + contrast_factor * local_contrast[..., np.newaxis] * image

    # Clip dei valori per mantenerli nell'intervallo 0-255
    enhanced_image = np.clip(enhanced_image, 0, 255).astype(np.uint8)

    return enhanced_image


# Creazione di un'immagine di test
image = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
a = timeit.timeit(lambda: enhance_contrast(image), number=1000)
print(f"Tempo di esecuzione: {a:.6f} secondi")
# Migliora il contrasto dell'immagine usando il metodo di Peli
enhanced_image = enhance_contrast(image)

# Visualizzazione dei risultati
plt.figure(figsize=(10, 5))

plt.subplot(1, 2, 1)
plt.title("Immagine Originale")
plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

plt.subplot(1, 2, 2)
plt.title("Immagine con Contrasto Migliorato")
plt.imshow(cv2.cvtColor(enhanced_image, cv2.COLOR_BGR2RGB))

plt.show()
