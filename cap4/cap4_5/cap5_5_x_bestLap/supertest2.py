import os
import time
import cProfile
import pstats
from random import randint

import cv2
import numpy as np

from cap4.cap4_5.cap5_5_x_bestLap.supertest2a import profile_function


def loadStingerFrames(path, split_func, merge_func, invert_func):
    stinger_frames = []
    alpha_frames = []
    inv_alpha_frames = []
    for filename in os.listdir(path):
        if filename.endswith('.png'):
            image_path = os.path.join(path, filename)
            image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
            b, g, r, a = split_func(image)
            overlay_image = merge_func([b, g, r])
            alpha = merge_func([a, a, a])
            invAlpha = merge_func([invert_func(a), invert_func(a), invert_func(a)])
            stinger_frames.append(np.ascontiguousarray(overlay_image))
            alpha_frames.append(np.ascontiguousarray(alpha))
            inv_alpha_frames.append(np.ascontiguousarray(invAlpha))
    return stinger_frames, alpha_frames, inv_alpha_frames


def splitNumpyIndex(image):
    return image[:, :, 0], image[:, :, 1], image[:, :, 2], image[:, :, 3]


def mergeListArray(channels):
    return np.array(channels).transpose(1, 2, 0)


def invertCv2(a):
    return cv2.bitwise_not(a)


def stingerFunction(_preview_frame, _program_frame, _stinger_frames, _alpha_frames, _inv_alphas):
    _wipePos = randint(0, len(_stinger_frames) - 1)
    alpha = _alpha_frames[_wipePos]
    invertAlpha = _inv_alphas[_wipePos]
    overlay_image = _stinger_frames[_wipePos]
    foreground = cv2.multiply(alpha, overlay_image)
    if _wipePos < len(_stinger_frames) // 2:
        background = cv2.multiply(invertAlpha, _preview_frame)
    else:
        background = cv2.multiply(invertAlpha, _program_frame)
    return cv2.add(foreground, background)

def profile_loadStingerFrames(path, split_func, merge_func, invert_func, name):
    profiler = cProfile.Profile()
    profiler.enable()
    result = loadStingerFrames(path, split_func, merge_func, invert_func)
    profiler.disable()
    profiler.dump_stats(f'stinger_load_stats_{name}')
    return result


def test():
    path = r'/cap5/cap5_5_StingerIdea\stingerTest'

    # Profiling delle funzioni di caricamento
    timeStart = time.time()
    stinger_frames, alpha_frames, inv_alphas = loadStingerFrames(path, cv2.split, cv2.merge, invertCv2)
    print(f"Time to load stinger frames (cv2.split, cv2.merge): {time.time() - timeStart:.4f} seconds")

    timeStart = time.time()
    stinger_frames2, alpha_frames2, inv_alphas2 = loadStingerFrames(path, splitNumpyIndex, cv2.merge, invertCv2)
    print(f"Time to load stinger frames2 (numpy index, cv2.merge): {time.time() - timeStart:.4f} seconds")

    timeStart = time.time()
    stinger_frames3, alpha_frames3, inv_alphas3 = loadStingerFrames(path, cv2.split, mergeListArray, invertCv2)
    print(f"Time to load stinger frames3 (cv2.split, numpy merge): {time.time() - timeStart:.4f} seconds")

    input1 = np.random.randint(0, 256, (1080, 1920, 3), dtype=np.uint8)
    input2 = np.random.randint(0, 256, (1080, 1920, 3), dtype=np.uint8)

    # Profiling delle funzioni di stinger
    result, profiler = profile_function(stingerFunction, input1, input2, stinger_frames, alpha_frames, inv_alphas)
    profiler.dump_stats('stinger_stats_original')

    result, profiler = profile_function(stingerFunction, input1, input2, stinger_frames2, alpha_frames2, inv_alphas2)
    profiler.dump_stats('stinger_stats_fast')

    result, profiler = profile_function(stingerFunction, input1, input2, stinger_frames3, alpha_frames3, inv_alphas3)
    profiler.dump_stats('stinger_stats_version3')

    # Visualizzazione dei risultati del profiling
    for stats_file in ['stinger_stats_original', 'stinger_stats_fast', 'stinger_stats_version3']:
        print(f"\nProfiling results for {stats_file}:")
        stats = pstats.Stats(stats_file)
        stats.strip_dirs()
        stats.sort_stats(pstats.SortKey.TIME)
        stats.print_stats(10)

    # Verifica contiguità dei dati
    print(f"stinger_frames contiguous: {np.all([frame.flags['C_CONTIGUOUS'] for frame in stinger_frames])}")
    print(f"stinger_frames2 contiguous: {np.all([frame.flags['C_CONTIGUOUS'] for frame in stinger_frames2])}")
    print(f"stinger_frames3 contiguous: {np.all([frame.flags['C_CONTIGUOUS'] for frame in stinger_frames3])}")


if __name__ == "__main__":
    test()
