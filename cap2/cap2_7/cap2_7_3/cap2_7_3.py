from timeit import timeit
import numpy as np

# Creazione delle matrici casuali
A = np.random.rand(1920, 1080)
B = np.random.rand(1920, 1080)

# Funzione per la moltiplicazione tradizionale con for loop
def traditional_multiplication(A, B):
    result = np.zeros(A.shape)
    for i in range(A.shape[0]):
        for j in range(A.shape[1]):
            result[i, j] = A[i, j] * B[i, j]
    return result


# Misurazione del tempo di esecuzione per la moltiplicazione vettorizzata
execution_time_vectorized = timeit(lambda: A * B, number=10)
print(f"Tempo di esecuzione per 10 esecuzioni della moltiplicazione vettorizzata: {execution_time_vectorized:.6f} secondi")

# Misurazione del tempo di esecuzione per la moltiplicazione tradizionale
execution_time_traditional = timeit(lambda: traditional_multiplication(A, B), number=10)
print(f"Tempo di esecuzione per 10 esecuzioni della moltiplicazione tradizionale: {execution_time_traditional:.6f} secondi")
