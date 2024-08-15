import cv2
import numpy as np
import timeit


# Metodo 1: Modifica Lineare del Contrasto
def adjust_contrast_linear(image, alpha=1.5, beta=0):
    return cv2.convertScaleAbs(image, alpha=alpha, beta=beta)


# Metodo 2: Regolazione Gamma
def adjust_contrast_gamma(image, gamma=1.0):
    inv_gamma = 1.0 / gamma
    table = np.array([(i / 255.0) ** inv_gamma * 255 for i in range(256)]).astype(np.uint8)
    return cv2.LUT(image, table)


def clahe(image, clip_limit=2.0, tile_grid_size=(8, 8)):
    channels = cv2.split(image)
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
    clahe_channels = [clahe.apply(channel) for channel in channels]
    return cv2.merge(clahe_channels)


def histogram_equalization(image):
    channels = cv2.split(image)
    eq_channels = [cv2.equalizeHist(channel) for channel in channels]
    return cv2.merge(eq_channels)


def clahe_yuv(image, clip_limit=2.0, tile_grid_size=(8, 8)):
    yuv_img = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
    yuv_img[:, :, 0] = clahe.apply(yuv_img[:, :, 0])
    return cv2.cvtColor(yuv_img, cv2.COLOR_YUV2BGR)


def histogram_equalization_yuv(image):
    yuv_img = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
    yuv_img[:, :, 0] = cv2.equalizeHist(yuv_img[:, :, 0])
    return cv2.cvtColor(yuv_img, cv2.COLOR_YUV2BGR)


def add_text_to_image(image, text):
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1
    color = (255, 255, 255)
    thickness = 2
    position = (10, 50)
    return cv2.putText(image, text, position, font, font_scale, color, thickness, cv2.LINE_AA)


# Genera un'immagine di test
image = cv2.imread(r"C:\pythonCode\openPyVisionBook\openPyVisionBook\cap3\cap3_6\lena_std.tif")

# Crea immagini con testo
original_with_text = add_text_to_image(image.copy(), "Original")
linear_with_text = add_text_to_image(adjust_contrast_linear(image, alpha=1.5, beta=20).copy(), "Linear Contrast")
gamma_with_text = add_text_to_image(adjust_contrast_gamma(image, gamma=1.2).copy(), "Gamma Adjustment")
clahe_with_text = add_text_to_image(clahe(image).copy(), "CLAHE")
hist_eq_with_text = add_text_to_image(histogram_equalization(image).copy(), "Histogram Equalization")
clahe_yuv_with_text = add_text_to_image(clahe_yuv(image).copy(), "CLAHE YUV")
hist_eq_yuv_with_text = add_text_to_image(histogram_equalization_yuv(image).copy(), "Histogram YUV")

# Crea un mosaico di immagini su due righe
first_row = np.hstack((original_with_text, linear_with_text, clahe_with_text, hist_eq_with_text))
second_row = np.hstack((original_with_text, gamma_with_text, clahe_yuv_with_text, hist_eq_yuv_with_text))
big_image = np.vstack((first_row, second_row))

# Visualizza i risultati
cv2.imshow("Contrast Adjustment", big_image)

# Test delle prestazioni
linear_test = timeit.timeit(lambda: adjust_contrast_linear(image, alpha=1.5, beta=20), number=1000)
gamma_test = timeit.timeit(lambda: adjust_contrast_gamma(image, gamma=1.2), number=1000)
clahe_test = timeit.timeit(lambda: clahe(image), number=1000)
hist_eq_test = timeit.timeit(lambda: histogram_equalization(image), number=1000)
clahe_yuv_test = timeit.timeit(lambda: clahe_yuv(image), number=1000)
hist_eq_yuv_test = timeit.timeit(lambda: histogram_equalization_yuv(image), number=1000)

print(f"Linear Contrast Adjustment: {linear_test:.2f} seconds for 1000 iterations = {linear_test / 1000:.4f} ms per iteration")
print(f"Gamma Adjustment: {gamma_test:.2f} seconds for 1000 iterations = {gamma_test / 1000:.4f} ms per iteration")
print(f"CLAHE: {clahe_test:.2f} seconds for 1000 iterations = {clahe_test / 1000:.4f} ms per iteration")
print(f"Histogram Equalization: {hist_eq_test:.2f} seconds for 1000 iterations = {hist_eq_test / 1000:.4f} ms per iteration")
print(f"CLAHE YUV: {clahe_yuv_test:.2f} seconds for 1000 iterations = {clahe_yuv_test / 1000:.4f} ms per iteration")
print(f"Histogram YUV: {hist_eq_yuv_test:.2f} seconds for 1000 iterations = {hist_eq_yuv_test / 1000:.4f} ms per iteration")
cv2.waitKey(0)
cv2.destroyAllWindows()
