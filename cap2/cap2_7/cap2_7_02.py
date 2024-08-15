from timeit import timeit


def payload():
   pass


timeIT = timeit(payload, number=10)
print(f"Tempo medio di esecuzione per 10 esecuzioni: {timeIT:.6f} secondi")