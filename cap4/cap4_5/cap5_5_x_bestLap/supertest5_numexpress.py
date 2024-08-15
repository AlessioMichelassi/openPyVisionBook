import os
import time
import timeit
import cProfile
import pstats
from random import randint
import cv2
import numpy as np
import numexpr as ne


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

    foreground = ne.evaluate("alpha * overlay_image")
    if _wipePos < len(_stinger_frames) // 2:
        background = ne.evaluate("invertAlpha * _preview_frame")
    else:
        background = ne.evaluate("invertAlpha * _program_frame")
    result = ne.evaluate("foreground + background")
    return result


def profile_function(func, *args, **kwargs):
    profiler = cProfile.Profile()
    profiler.enable()
    result = func(*args, **kwargs)
    profiler.disable()
    return result, profiler


def profile_loadStingerFrames(path, split_func, merge_func, invert_func, name):
    profiler = cProfile.Profile()
    profiler.enable()
    result = loadStingerFrames(path, split_func, merge_func, invert_func)
    profiler.disable()
    profiler.dump_stats(f'stinger_load_stats_{name}')
    return result


def test():
    path = r'C:\pythonCode\openPyVisionBook\openPyVisionBook\cap5\cap5_5\stingerTest'

    # Profiling delle funzioni di caricamento
    timeStart = time.time()
    stinger_frames, alpha_frames, inv_alphas = profile_loadStingerFrames(path, cv2.split, cv2.merge, invertCv2,
                                                                         "original")
    print(f"Time to load stinger frames (cv2.split, cv2.merge): {time.time() - timeStart:.4f} seconds")

    timeStart = time.time()
    stinger_frames2, alpha_frames2, inv_alphas2 = profile_loadStingerFrames(path, splitNumpyIndex, cv2.merge, invertCv2,
                                                                            "fast")
    print(f"Time to load stinger frames2 (numpy index, cv2.merge): {time.time() - timeStart:.4f} seconds")

    timeStart = time.time()
    stinger_frames3, alpha_frames3, inv_alphas3 = profile_loadStingerFrames(path, splitNumpyIndex, mergeListArray,
                                                                            invertCv2, "version3")
    print(f"Time to load stinger frames3 (splitNumpyIndex, numpy merge): {time.time() - timeStart:.4f} seconds")

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
    for stats_file in ['stinger_load_stats_original', 'stinger_load_stats_fast', 'stinger_load_stats_version3',
                       'stinger_stats_original', 'stinger_stats_fast', 'stinger_stats_version3']:
        print(f"\nProfiling results for {stats_file}:")
        stats = pstats.Stats(stats_file)
        stats.strip_dirs()
        stats.sort_stats(pstats.SortKey.TIME)
        stats.print_stats(10)

    # Verifica contiguità dei dati
    print(f"stinger_frames contiguous: {np.all([frame.flags['C_CONTIGUOUS'] for frame in stinger_frames])}")
    print(f"stinger_frames2 contiguous: {np.all([frame.flags['C_CONTIGUOUS'] for frame in stinger_frames2])}")
    print(f"stinger_frames3 contiguous: {np.all([frame.flags['C_CONTIGUOUS'] for frame in stinger_frames3])}")

    # Test delle performance per stingerFunction (1000 iterazioni)
    timeStringerFunction = timeit.timeit(
        lambda: stingerFunction(input1, input2, stinger_frames, alpha_frames, inv_alphas),
        number=1000)
    print(f"Execution time of stingerFunction (original): {timeStringerFunction:.4f} seconds")

    timeStringerFunctionFast = timeit.timeit(
        lambda: stingerFunction(input1, input2, stinger_frames2, alpha_frames2, inv_alphas2),
        number=1000)
    print(f"Execution time of stingerFunction (fast): {timeStringerFunctionFast:.4f} seconds")

    timeStringerFunction3 = timeit.timeit(
        lambda: stingerFunction(input1, input2, stinger_frames3, alpha_frames3, inv_alphas3),
        number=1000)
    print(f"Execution time of stingerFunction (version3): {timeStringerFunction3:.4f} seconds")


if __name__ == "__main__":
    test()
