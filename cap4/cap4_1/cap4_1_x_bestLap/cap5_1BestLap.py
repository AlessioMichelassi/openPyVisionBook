import timeit
import cv2
import numpy as np


def addWeightCv2(img1, img2, alpha):
    return cv2.addWeighted(img1, alpha, img2, 1 - alpha, 0)


def addWeightNumpy(img1, img2, alpha):
    img1_float = img1.astype(np.float32)*alpha
    img2_float = img2.astype(np.float32)*(1-alpha)
    result = np.add(img1_float, img2_float)
    return np.clip(result, 0, 255).astype(np.uint8)


def addWeightNumpy2(img1, img2, alpha):
    result = np.add(np.multiply(img1.astype(np.float32), alpha), np.multiply(img2.astype(np.float32), 1 - alpha))
    return np.clip(result, 0, 255).astype(np.uint8)


input1 = np.random.randint(0, 256, (1920, 1080, 3), dtype=np.uint8)
input2 = np.random.randint(0, 256, (1920, 1080, 3), dtype=np.uint8)

print("bestLap Start")
print("OpenCV")
cv2Time = timeit.timeit(lambda: addWeightCv2(input1, input2, 0.5), number=100)
print(cv2Time)
print("Numpy")
numpyTime = timeit.timeit(lambda: addWeightNumpy(input1, input2, 0.5), number=100)
print(numpyTime)
print("Numpy2")
numpyTime2 = timeit.timeit(lambda: addWeightNumpy2(input1, input2, 0.5), number=100)
print(numpyTime2)

"""cv2.imshow("input1", input1)
cv2.imshow("input2", input2)
cv2.imshow("cv2", addWeightCv2(input1, input2, 0.5))
cv2.imshow("numpy", addWeightNumpy(input1, input2, 0.5))
cv2.imshow("numpy2", addWeightNumpy2(input1, input2, 0.5))
cv2.waitKey(0)"""
