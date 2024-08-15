import cv2
import numpy as np
import matplotlib.pyplot as plt


def create_low_contrast_image(size=(100, 100), base_intensity=128, noise_level=10):
    """
    Crea un'immagine a basso contrasto.

    size: dimensioni dell'immagine (altezza, larghezza)
    base_intensity: valore medio dei pixel
    noise_level: livello di rumore per aggiungere variazioni minime
    """
    # Crea un'immagine con un valore medio uniforme di pixel
    low_contrast_image = np.full(size + (3,), base_intensity, dtype=np.uint8)

    # Aggiungi un rumore molto piccolo per simulare un basso contrasto
    noise = np.random.randint(-noise_level, noise_level + 1, size + (3,), dtype=np.int16)
    low_contrast_image = np.clip(low_contrast_image + noise, 0, 255).astype(np.uint8)

    return low_contrast_image


# Funzione per calcolare il contrasto locale usando il metodo di Peli
def compute_local_contrast(image, window_size=3):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY).astype(np.float32)
    kernel = np.ones((window_size, window_size), np.float32) / (window_size ** 2)
    local_mean = cv2.filter2D(gray_image, -1, kernel)
    local_contrast = (gray_image - local_mean) / (gray_image + local_mean + 1e-6)
    return local_contrast


# Funzione per migliorare il contrasto dell'immagine
def enhance_contrast(image, contrast_factor=1.5):
    local_contrast = compute_local_contrast(image)
    enhanced_image = image.astype(np.float32) + contrast_factor * local_contrast[..., np.newaxis] * image
    enhanced_image = np.clip(enhanced_image, 0, 255).astype(np.uint8)
    return enhanced_image


# Creazione di un'immagine a basso contrasto
low_contrast_image = create_low_contrast_image(size=(100, 100), base_intensity=128, noise_level=10)

# Applicazione dell'algoritmo di miglioramento del contrasto
enhanced_image = enhance_contrast(low_contrast_image)

# Visualizzazione dei risultati
plt.figure(figsize=(10, 5))

plt.subplot(1, 2, 1)
plt.title("Immagine a Basso Contrasto")
plt.imshow(cv2.cvtColor(low_contrast_image, cv2.COLOR_BGR2RGB))

plt.subplot(1, 2, 2)
plt.title("Immagine con Contrasto Migliorato")
plt.imshow(cv2.cvtColor(enhanced_image, cv2.COLOR_BGR2RGB))

plt.show()
