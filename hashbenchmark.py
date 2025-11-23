import hashlib, time
from argon2 import PasswordHasher
import pandas as pd

results = []
password = "SuperSecure123!".encode()
ph = PasswordHasher()
start_wall = time.time()
start_cpu = time.process_time()
for _ in range(100000):
    hashlib.sha256(password).hexdigest()
sha256_wall = time.time() - start_wall
sha256_cpu = time.process_time() - start_cpu

start_wall = time.time()
start_cpu = time.process_time()
for _ in range(50):
    ph.hash("SuperSecure123!")
argon2_wall = time.time() - start_wall
argon2_cpu = time.process_time() - start_cpu

results.append({
    "SHA256_wall": sha256_wall,
    "SHA256_CPU": sha256_cpu,
    "argon2_wall": argon2_wall,
    "argon2_CPU": argon2_cpu,
    "SHA256_time_per_hash": sha256_wall / 100000,
    "argon2_time_per_hash": argon2_wall / 50
})

df = pd.DataFrame(results)
print(df)

