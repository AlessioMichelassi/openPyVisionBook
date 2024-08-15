import os
import time
import timeit
from random import randint

import cv2
import numpy as np


def splitNumpyIndex(image):
    b = image[:, :, 0]
    g = image[:, :, 1]
    r = image[:, :, 2]
    a = image[:, :, 3]
    return b, g, r, a


def splitListComprehension(image):
    b, g, r, a = [image[:, :, i] for i in range(4)]
    return b, g, r, a


def splitCv2Split(image):
    b, g, r, a = cv2.split(image)
    return b, g, r, a


def splitNumpySlice(image):
    b, g, r, a = [image[:, :, i] for i in range(4)]
    return b, g, r, a


def mergeListToArray(b, g, r):
    return np.array([b, g, r]).transpose(1, 2, 0)


def mergeCv2Merge(b, g, r, a):
    return cv2.merge([b, g, r, a])


def loadStingerFrames(path):
    stinger_frames = []
    alpha_frames = []
    inv_alpha_frames = []
    for filename in os.listdir(path):
        if filename.endswith('.png'):
            image_path = os.path.join(path, filename)
            image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)  # Legge anche il canale alpha
            b, g, r, a = cv2.split(image)
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
            image_path = os.path.join(path, filename)
            image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)  # Legge anche il canale alpha
            b, g, r, a = splitNumpyIndex(image)
            overlay_image = cv2.merge((b, g, r))
            alpha = cv2.merge((a, a, a))
            invA = cv2.bitwise_not(a)
            invAlpha = cv2.merge((invA, invA, invA))
            stinger_frames.append(overlay_image)
            alpha_frames.append(alpha)
            inv_alpha_frames.append(invAlpha)
    return stinger_frames, alpha_frames, inv_alpha_frames


def loadStingerFrames3(path):
    stinger_frames = []
    alpha_frames = []
    inv_alpha_frames = []
    for filename in os.listdir(path):
        if filename.endswith('.png'):
            image_path = os.path.join(path, filename)
            image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)  # Legge anche il canale alpha
            b, g, r, a = splitListComprehension(image)
            overlay_image = mergeListToArray(b, g, r)
            alpha = mergeCv2Merge(a, a, a)
            invA = cv2.bitwise_not(a)
            invAlpha = mergeCv2Merge(invA, invA, invA, invA)
            stinger_frames.append(overlay_image)
            alpha_frames.append(alpha)
            inv_alpha_frames.append(invAlpha)
    return stinger_frames, alpha_frames, inv_alpha_frames


def loadStingerFrames4(path):
    stinger_frames = []
    alpha_frames = []
    inv_alpha_frames = []
    for filename in os.listdir(path):
        if filename.endswith('.png'):
            image_path = os.path.join(path, filename)
            image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)  # Legge anche il canale alpha
            b, g, r, a = splitCv2Split(image)
            overlay_image = cv2.merge((b, g, r))
            alpha = cv2.merge((a, a, a))
            invA = cv2.bitwise_not(a)
            invAlpha = cv2.merge((invA, invA, invA))
            stinger_frames.append(overlay_image)
            alpha_frames.append(alpha)
            inv_alpha_frames.append(invAlpha)
    return stinger_frames, alpha_frames, inv_alpha_frames


def checkImageListEquality(list1, list2):
    if len(list1) != len(list2):
        return False
    for i in range(len(list1)):
        if not np.array_equal(list1[i], list2[i]):
            return False
    return True


def checkWathFailed(list1, list2):
    for n in range(len(list1)):
        if not np.array_equal(list1[n], list2[n]):
            print(f"Failed at index {n}")
            print(f"list1: {list1[n]}")
            print(f"list2: {list2[n]}")
            cv2.imshow("list1", list1[n])
            cv2.imshow("list2", list2[n])
            cv2.waitKey(0)
            return False
    cv2.imshow("list1", list1[10])
    cv2.imshow("list2", list2[10])
    cv2.waitKey(0)


def test():
    path = r'C:\pythonCode\openPyVisionBook\openPyVisionBook\cap5\cap5_5\stingerTest'
    startTime = time.time()
    stinger_frames1, alpha_frames1, inv_alpha_frames1 = loadStingerFrames(path)
    print(f"Time elapsed for loadStingerFrames: {time.time() - startTime}")
    stinger_frames2, alpha_frames2, inv_alpha_frames2 = loadStingerFrames2(path)
    print(f"Time elapsed for loadStingerFrames2: {time.time() - startTime}")
    stinger_frames3, alpha_frames3, inv_alpha_frames3 = loadStingerFrames3(path)
    print(f"Time elapsed for loadStingerFrames3: {time.time() - startTime}")
    stinger_frames4, alpha_frames4, inv_alpha_frames4 = loadStingerFrames4(path)
    print(f"Time elapsed for loadStingerFrames4: {time.time() - startTime}")
    if not checkImageListEquality(stinger_frames1, stinger_frames2):
        print("stinger_frames1 and stinger_frames2 are different.")
        print(
            f"stinger_frames1: len= {len(stinger_frames1)}, dtipe 0= {stinger_frames1[0].dtype}, shape 0= {stinger_frames1[0].shape}")
        print(
            f"stinger_frames2: len= {len(stinger_frames2)}, dtipe 0= {stinger_frames2[0].dtype}, shape 0= {stinger_frames2[0].shape}")
        checkWathFailed(stinger_frames1, stinger_frames2)
    if not checkImageListEquality(stinger_frames1, stinger_frames3):
        print(
            f"stinger_frames1: len= {len(stinger_frames1)}, dtipe 0= {stinger_frames1[0].dtype}, shape 0= {stinger_frames1[0].shape}")
        print(
            f"stinger_frames3: len= {len(stinger_frames3)}, dtipe 0= {stinger_frames3[0].dtype}, shape 0= {stinger_frames3[0].shape}")
        print("stinger_frames1 and stinger_frames3 are different.")
        checkWathFailed(stinger_frames1, stinger_frames2)
    if not checkImageListEquality(stinger_frames1, stinger_frames4):
        print(
            f"stinger_frames1: len= {len(stinger_frames1)}, dtipe 0= {stinger_frames1[0].dtype}, shape 0= {stinger_frames1[0].shape}")
        print(
            f"stinger_frames4: len= {len(stinger_frames4)}, dtipe 0= {stinger_frames4[0].dtype}, shape 0= {stinger_frames4[0].shape}")
        print("stinger_frames1 and stinger_frames4 are different.")
        checkWathFailed(stinger_frames1, stinger_frames2)
    if not checkImageListEquality(alpha_frames1, alpha_frames2):
        print(
            f"alpha_frames1: len= {len(alpha_frames1)}, dtipe 0= {alpha_frames1[0].dtype}, shape 0= {alpha_frames1[0].shape}")
        print(
            f"alpha_frames2: len= {len(alpha_frames2)}, dtipe 0= {alpha_frames2[0].dtype}, shape 0= {alpha_frames2[0].shape}")
        print("alpha_frames1 and alpha_frames2 are different.")
        checkWathFailed(stinger_frames1, stinger_frames2)
    if not checkImageListEquality(alpha_frames1, alpha_frames3):
        print(
            f"alpha_frames1: len= {len(alpha_frames1)}, dtipe 0= {alpha_frames1[0].dtype}, shape 0= {alpha_frames1[0].shape}")
        print(
            f"alpha_frames3: len= {len(alpha_frames3)}, dtipe 0= {alpha_frames3[0].dtype}, shape 0= {alpha_frames3[0].shape}")
        print("alpha_frames1 and alpha_frames3 are different.")
        checkWathFailed(stinger_frames1, stinger_frames2)
    if not checkImageListEquality(alpha_frames1, alpha_frames4):
        print(
            f"alpha_frames1: len= {len(alpha_frames1)}, dtipe 0= {alpha_frames1[0].dtype}, shape 0= {alpha_frames1[0].shape}")
        print(
            f"alpha_frames4: len= {len(alpha_frames4)}, dtipe 0= {alpha_frames4[0].dtype}, shape 0= {alpha_frames4[0].shape}")
        print("alpha_frames1 and alpha_frames4 are different.")
    if not checkImageListEquality(inv_alpha_frames1, inv_alpha_frames2):
        print("inv_alpha_frames1 and inv_alpha_frames2 are different.")
    if not checkImageListEquality(inv_alpha_frames1, inv_alpha_frames3):
        print("inv_alpha_frames1 and inv_alpha_frames3 are different.")
    if not checkImageListEquality(inv_alpha_frames1, inv_alpha_frames4):
        print("inv_alpha_frames1 and inv_alpha_frames4 are different.")

    print("All tests passed successfully.")


if __name__ == "__main__":
    if test():
        print("All tests passed successfully.")
    else:
        print("Some tests failed.")
