import cv2
import numpy as np

imagePath = r"C:\pythonCode\openPyVisionBook\openPyVisionBook\cap4\cap4_5\stingerTest\Untitled00216035.png"
overlay_image_full = cv2.imread(imagePath, cv2.IMREAD_UNCHANGED)
b, g, r, a = cv2.split(overlay_image_full)
overlay = cv2.merge((b, g, r))
alpha = cv2.merge((a, a, a))
iA = cv2.bitwise_not(alpha)
alphaNormalized = alpha / 255.0
invertAlphaNormalized = 1 - alphaNormalized
premultOverlay = cv2.multiply(overlay, alphaNormalized, dtype=cv2.CV_8U)
randomNoise = np.random.randint(0, 256, (1080, 1920, 3), dtype=np.uint8)
premultRandomNoise = cv2.multiply(randomNoise, invertAlphaNormalized, dtype=cv2.CV_8U)
finalresult = cv2.add(premultOverlay, premultRandomNoise)
cv2.imshow("overlay_image_full", overlay_image_full)
cv2.imshow("overlay", premultRandomNoise)
cv2.imshow("premultOverlay", premultOverlay)
cv2.imshow("alpha", alpha)
cv2.imshow("iA", iA)
cv2.imshow("finalresult", finalresult)
cv2.waitKey(0)