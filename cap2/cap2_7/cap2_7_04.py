import cProfile


def slow_function_optimized():
    total = 0
    for i in range(10000):
        total += sum(range(100))
    return total


def main_optimized():
    result = slow_function_optimized()
    print(result)


cProfile.run('main_optimized()')
