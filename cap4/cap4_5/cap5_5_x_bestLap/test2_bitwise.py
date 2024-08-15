import cv2
import numpy as np
import time

# Impostazione iniziale (questa parte viene eseguita una sola volta)
img1 = np.full((1080, 1920, 3), (0, 0, 255), dtype=np.uint8)  # Immagine rossa
mask = np.zeros((1080, 1920), dtype=np.uint8)
mask[480:1440, 270:810] = 255
mask = cv2.GaussianBlur(mask, (51, 51), 0)

# Precalcolo di img1 * mask
mask_float = mask.astype(float) / 255.0
mask_3channel = cv2.merge([mask_float, mask_float, mask_float])
precalc_img1_masked = cv2.multiply(img1, mask_3channel, dtype=cv2.CV_8U)

# Precalcolo della maschera inversa
inv_mask_3channel = cv2.merge([1 - mask_float, 1 - mask_float, 1 - mask_float])
# Supponiamo che img2 cambi ad ogni frame (in questo esempio è statica per semplicità)
img2 = np.full((1080, 1920, 3), (255, 0, 0), dtype=np.uint8)  # Immagine blu

# Questa parte verrebbe eseguita per ogni frame
timeStart = time.time()


# Calcola img2 * inv_mask
img2_masked = cv2.multiply(img2, inv_mask_3channel, dtype=cv2.CV_8U)

# Somma le due matrici precalcolate
result = cv2.add(precalc_img1_masked, img2_masked)

timeEnd = time.time()
print("Time elapsed: ", (timeEnd - timeStart), "s")


# Mostra l'ultimo risultato
cv2.imshow('Result', result)
cv2.waitKey(0)
cv2.destroyAllWindows()