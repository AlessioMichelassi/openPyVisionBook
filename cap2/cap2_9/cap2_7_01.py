from timeit import timeit


def op1():
    for x in range(1, 1920):
        for y in range(1, 1080):
            pass  # Fai qualcosa qui, ad esempio: z = x * y


# Misura il tempo di esecuzione della funzione `op1` con 10 esecuzioni
execution_time = timeit(op1, number=10)
print(f"Tempo di esecuzione per 10 esecuzioni di op1: {execution_time:.6f} secondi")
