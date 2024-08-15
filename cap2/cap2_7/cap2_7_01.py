import time


def payload():
   pass


start = time.time()
payload() # eseguiamo un carico
print(f"Tempo di esecuzione: {time.time() - start:.6f} secondi")