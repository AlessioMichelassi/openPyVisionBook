import os
import time
import timeit
from random import randint

import cv2
import numpy as np


def numpy_index_4ch(image):
    b = image[:, :, 0]
    g = image[:, :, 1]
    r = image[:, :, 2]
    a = image[:, :, 3]
    return b, g, r, a


def list_to_array(b, g, r):
    image = np.array([r, g, b]).transpose(1, 2, 0)
    return image


def list_comprehension_4ch(image):
    b, g, r, a = [image[:, :, i] for i in range(4)]
    return b, g, r, a


def loadStingerFrames(path):
    stinger_frames = []
    alpha_frames = []
    inv_alpha_frames = []
    for filename in os.listdir(path):
        if filename.endswith('.png'):
            image_path = os.path.join(path, filename)
            image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)  # Legge anche il canale alpha
            b, g, r, a = numpy_index_4ch(image)
            overlay_image = cv2.merge((b, g, r))
            stinger_frames.append(overlay_image)
            alpha_frames.append(cv2.merge((a, a, a)))
            invAlpha = cv2.merge((cv2.bitwise_not(a), cv2.bitwise_not(a), cv2.bitwise_not(a)))
            inv_alpha_frames.append(invAlpha)
    return stinger_frames, alpha_frames, inv_alpha_frames


def loadStingerFrames2(path):
    stinger_frames = []
    alpha_frames = []
    inv_alpha_frames = []
    for filename in os.listdir(path):
        if filename.endswith('.png'):
            startTime = time.time()
            image_path = os.path.join(path, filename)
            image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)  # Legge anche il canale alpha

            b, g, r, a = list_comprehension_4ch(image)
            overlay_image = list_to_array(b, g, r)
            alpha = list_to_array(a, a, a)
            invA = cv2.bitwise_not(a)
            invAlpha = list_to_array(invA, invA, invA)
            stinger_frames.append(overlay_image)
            alpha_frames.append(alpha)
            inv_alpha_frames.append(invAlpha)
    return stinger_frames, alpha_frames, inv_alpha_frames


def loadStingerFramesOptimized(path):
    stinger_frames = []
    alpha_frames = []
    inv_alpha_frames = []
    for filename in os.listdir(path):
        if filename.endswith('.png'):
            image_path = os.path.join(path, filename)
            image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)  # Legge anche il canale alpha
            b, g, r, a = numpy_index_4ch(image)
            overlay_image = cv2.merge((b, g, r))  # Usare cv2.merge per mantenere l'efficienza di OpenCV
            alpha = cv2.merge((a, a, a))
            invAlpha = cv2.merge((255 - a, 255 - a, 255 - a))
            stinger_frames.append(overlay_image)
            alpha_frames.append(alpha)
            inv_alpha_frames.append(invAlpha)
    return stinger_frames, alpha_frames, inv_alpha_frames


def stingerFunction(preview_frame, program_frame, stinger_frames, alpha_frames, inv_alphas):
    _wipePos = randint(0, len(stinger_frames) - 1)
    alpha = alpha_frames[_wipePos]
    invertAlpha = inv_alphas[_wipePos]
    overlay_image = stinger_frames[_wipePos]
    startTime = time.time()
    foreground = cv2.multiply(alpha, overlay_image)
    #print(f"Time to multiply alpha and overlay_image: {time.time() - startTime}")
    if _wipePos < len(stinger_frames) // 2:
        background = cv2.multiply(invertAlpha, preview_frame)
    else:
        background = cv2.multiply(invertAlpha, program_frame)
    addImage = cv2.add(foreground, background)
    #print(f"Time to add foreground and background: {time.time() - startTime}")
    return addImage


def compare_frames(frames1, frames2):
    for f1, f2 in zip(frames1, frames2):
        if not np.array_equal(f1, f2):
            return False
    return True


def test_performance():
    input1 = np.random.randint(0, 256, (1080, 1920, 3), dtype=np.uint8)
    input2 = np.random.randint(0, 256, (1080, 1920, 3), dtype=np.uint8)

    # Caricamento delle immagini
    timeStart = time.time()
    stinger_frames, alpha_frames, inv_alphas = loadStingerFrames(
        r"C:\pythonCode\openPyVisionBook\openPyVisionBook\cap5\cap5_5\stingerTest")
    load_time_1 = time.time() - timeStart
    print(f"Time to load stinger frames: {load_time_1} seconds")

    # Test delle performance per stingerFunction
    timeStringerFunction = timeit.timeit(
        lambda: stingerFunction(input1, input2, stinger_frames, alpha_frames, inv_alphas),
        number=1000)
    print(f"Execution time of stingerFunction with loadStingerFrames: {timeStringerFunction} seconds")

    # Caricamento delle immagini con il secondo metodo
    timeStart = time.time()
    stinger_frames2, alpha_frames2, inv_alphas2 = loadStingerFrames2(
        r"C:\pythonCode\openPyVisionBook\openPyVisionBook\cap5\cap5_5\stingerTest")
    load_time_2 = time.time() - timeStart
    print(f"Time to load stinger frames2: {load_time_2} seconds")

    # Test delle performance per stingerFunction
    timeStringerFunction2 = timeit.timeit(
        lambda: stingerFunction(input1, input2, stinger_frames2, alpha_frames2, inv_alphas2),
        number=1000)
    print(f"Execution time of stingerFunction with loadStingerFrames2: {timeStringerFunction2} seconds")

    # Confronto delle immagini
    if compare_frames(stinger_frames, stinger_frames2) and compare_frames(alpha_frames,
                                                                          alpha_frames2) and compare_frames(inv_alphas,
                                                                                                            inv_alphas2):
        print("Le immagini caricate sono identiche.")
    else:
        print("Le immagini caricate differiscono.")
        # crea un mosaico di immagini per visualizzare le differenze
        diff_images = np.concatenate((stinger_frames, stinger_frames2), axis=1)

        cv2.imshow("Differenze tra le immagini caricate", diff_images)
        cv2.waitKey(0)


if __name__ == "__main__":
    test_performance()
