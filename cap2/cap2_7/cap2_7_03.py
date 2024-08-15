import cProfile


def slow_function():
    total = 0
    for i in range(10000):
        total += sum(j for j in range(100))
    return total


def main():
    result = slow_function()
    print(result)


if __name__ == "__main__":
    cProfile.run('main()')
