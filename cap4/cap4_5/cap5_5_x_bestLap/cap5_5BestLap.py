import os
import time
import timeit
from random import random, randint

import cv2
import numpy as np

"""
OPERATION SPEED TESTED:
INVERT:
    OpenCV inversion duration: 0.120458 seconds
    Bitwise inversion duration: 0.218525 seconds
    255 - image inversion duration: 0.226272 seconds
SPLIT:
    numpy_index_4ch: 0.005418 seconds
    numpy_split_4ch: 0.057531 seconds
    list_comprehension_4ch: 0.007197 seconds
    numpy_dsplit_4ch: 0.059373 seconds
    numpy_moveaxis_4ch: 0.021403 seconds
    small_opencv_split: 34.294690 seconds
MERGE:
    list_to_array: 1.288917 seconds
    opencv_merge: 1.613998 seconds
    numpy_stack: 3.311415 seconds
    numpy_dstack: 3.297586 seconds
    numpy_concatenate: 3.262816 seconds
    manual_assignment: 3.479700 seconds

"""


def numpy_index_4ch(image):
    b = image[:, :, 0]
    g = image[:, :, 1]
    r = image[:, :, 2]
    a = image[:, :, 3]
    return b, g, r, a


def list_to_array(b, g, r):
    return np.array([b, g, r]).transpose(1, 2, 0)


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


def stingerFunction1(preview_frame, program_frame, stinger_frames, alpha_frames):  # from Alessio!
    _wipePos = randint(0, len(stinger_frames) - 1)
    a = alpha_frames[_wipePos]
    overlay_image = stinger_frames[_wipePos]
    iA = cv2.bitwise_not(a)
    alpha = cv2.merge((a, a, a))
    invertAlpha = cv2.merge((iA, iA, iA))
    foreground = cv2.multiply(alpha, overlay_image)
    if _wipePos < len(stinger_frames) // 2:
        background = cv2.multiply(invertAlpha, preview_frame)
    else:
        background = cv2.multiply(invertAlpha, program_frame)
    return cv2.add(foreground, background)


def stingerFunction2(preview_frame, program_frame, stinger_frames, alpha_frames):  # from chat gpt!
    _wipePos = randint(0, len(stinger_frames) - 1)
    a = alpha_frames[_wipePos]
    overlay_image = stinger_frames[_wipePos]

    # Utilizzare operazioni bitwise per moltiplicazione e somma
    alpha = cv2.merge((a, a, a))
    invertAlpha = cv2.merge((cv2.bitwise_not(a), cv2.bitwise_not(a), cv2.bitwise_not(a)))

    foreground = cv2.bitwise_and(overlay_image, alpha)
    if _wipePos < len(stinger_frames) // 2:
        background = cv2.bitwise_and(preview_frame, invertAlpha)
    else:
        background = cv2.bitwise_and(program_frame, invertAlpha)

    return cv2.add(foreground, background)


def stingerFunction3(preview_frame, program_frame, stinger_frames, alpha_frames, inv_alphas):  # from Alessio!
    _wipePos = randint(0, len(stinger_frames) - 1)
    alpha = alpha_frames[_wipePos]
    invertAlpha = inv_alphas[_wipePos]
    overlay_image = stinger_frames[_wipePos]
    foreground = cv2.multiply(alpha, overlay_image)
    if _wipePos < len(stinger_frames) // 2:
        background = cv2.multiply(invertAlpha, preview_frame)
    else:
        background = cv2.multiply(invertAlpha, program_frame)
    return cv2.add(foreground, background)


def stingerFunctionFast(preview_frame, program_frame, stinger_frames, alpha_frames, inv_alphas):  # from chat gpt!
    _wipePos = randint(0, len(stinger_frames) - 1)
    alpha = alpha_frames[_wipePos]
    invertAlpha = inv_alphas[_wipePos]
    overlay_image = stinger_frames[_wipePos]
    a = alpha[:, :, 0]  # Utilizzare solo un canale per la maschera
    iA = invertAlpha[:, :, 0]
    # Utilizzare operazioni bitwise per applicare le maschere
    foreground = cv2.bitwise_and(overlay_image, overlay_image, mask=a)
    if _wipePos < len(stinger_frames) // 2:
        background = cv2.bitwise_and(preview_frame, preview_frame, mask=iA)
    else:
        background = cv2.bitwise_and(program_frame, program_frame, mask=iA)

    return cv2.add(foreground, background)


# Esempio di utilizzo
# input1 e input2 sono i frame di anteprima e programma
# stinger_frames è una lista di frame per l'animazione di stinger
# wipe è l'indice del frame corrente nell'animazione di stinger

input1 = np.random.randint(0, 256, (1080, 1920, 3), dtype=np.uint8)
input2 = np.random.randint(0, 256, (1080, 1920, 3), dtype=np.uint8)
timeStart = time.time()
stinger_frames, alpha_frames, inv_alphas = loadStingerFrames(
    r"C:\pythonCode\openPyVisionBook\openPyVisionBook\cap5\cap5_5\stingerTest")
print(f"Time to load stinger frames: {time.time() - timeStart} seconds")
"""
timeStringerFunction1 = timeit.timeit(lambda: stingerFunction1(input1, input2, stinger_frames, alpha_frames),
                                      number=1000)  # 0.008
print(f"Execution time of stingerFunction1: {timeStringerFunction1} seconds")

timeStringerFunction2 = timeit.timeit(lambda: stingerFunction2(input1, input2, stinger_frames, alpha_frames),
                                      number=1000)  # 0.006
print(f"Execution time of stingerFunction2: {timeStringerFunction2} seconds")
"""
timeStringerFunction3 = timeit.timeit(
    lambda: stingerFunction3(input1, input2, stinger_frames, alpha_frames, inv_alphas),
    number=1000)  # 0.006
print(f"Execution time of stingerFunction3: {timeStringerFunction3} seconds")

timeStringerFunctionFast = timeit.timeit(
    lambda: stingerFunctionFast(input1, input2, stinger_frames, alpha_frames, inv_alphas),
    number=1000)  # 0.006

print(f"Execution time of stingerFunctionFast: {timeStringerFunctionFast} seconds")
