import hashlib
from argon2 import PasswordHasher, Type

ph = PasswordHasher(
    time_cost=3, 
    memory_cost =65536,
    parallelism=1,
    hash_len=32,
    salt_len=16, 
    type=Type.ID
)  
    
with open("passwords.txt", "r") as file, \
     open("argon2.hash", "w") as f_argon, \
     open("sha256.hash", "w") as f_sha:

    for line in file:
        password = line.strip()
        if not password:
            continue

        # SHA256
        sha256_hash = hashlib.sha256(password.encode()).hexdigest()
        f_sha.write(sha256_hash + "\n")

        # Argon2id
        argon2_hash = ph.hash(password)
        f_argon.write(argon2_hash + "\n")

