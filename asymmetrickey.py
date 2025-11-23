from cryptography.hazmat.primitives.asymmetric import rsa, ec
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
import time, timeit
import pandas as pd
from matplotlib import pyplot as plt
rsa_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
ecc_key = ec.generate_private_key(ec.SECP256R1())

results_keygen = [] 

start_wall = time.time()
start_cpu= time.process_time()
for _ in range(200): 
    rsa.generate_private_key(public_exponent=65537, key_size=2048)
rsa_keygen_wall = time.time() - start_wall
rsa_keygen_cpu = time.process_time() - start_cpu

start_wall = time.time()
start_cpu= time.process_time()
for _ in range (200):
    ec.generate_private_key(ec.SECP256R1())
ecc_keygen_wall = time.time() - start_wall
ecc_keygen_cpu = time.process_time() - start_cpu

results_keygen.append({
    "RSA_keygen_wall": rsa_keygen_wall,
    "RSA_keygen_cpu": rsa_keygen_cpu,
    "ECC_keygen_wall": ecc_keygen_wall,
    "ECC_keygen_cpu": ecc_keygen_cpu
})

df = pd.DataFrame(results_keygen)
print(df)

#signing time benchmark
results_signing = []
message = b"A" * 1024

# --- RSA Signing ---
start_wall = time.time()
start_cpu = time.process_time()
for _ in range(1000):
    rsa_key.sign(message, padding.PKCS1v15(), hashes.SHA256())
rsa_sign_wall = time.time() - start_wall
rsa_sign_cpu = time.process_time() - start_cpu

# --- ECC Signing ---
start_wall = time.time()
start_cpu = time.process_time()
for _ in range(1000):
    ecc_key.sign(message, ec.ECDSA(hashes.SHA256()))
ecc_sign_wall = time.time() - start_wall
ecc_sign_cpu = time.process_time() - start_cpu

results_signing.append({
    "RSA_sign_wall": rsa_sign_wall,
    "RSA_sign_cpu": rsa_sign_cpu,
    "ECC_sign_wall": ecc_sign_wall,
    "ECC_sign_cpu": ecc_sign_cpu
})

df = pd.DataFrame(results_signing)
print(df)

#verification time
results_verification = [] 
rsa_sig = rsa_key.sign(message, padding.PKCS1v15(), hashes.SHA256())
ecc_sig = ecc_key.sign(message, ec.ECDSA(hashes.SHA256()))

# --- RSA Verify ---
start_wall = time.time()
start_cpu = time.process_time()
for _ in range(1000):
    rsa_key.public_key().verify(
        rsa_sig, message, padding.PKCS1v15(), hashes.SHA256()
    )
rsa_verify_wall = time.time() - start_wall
rsa_verify_cpu = time.process_time() - start_cpu

# --- ECC Verify ---
start_wall = time.time()
start_cpu = time.process_time()
for _ in range(1000):
    ecc_key.public_key().verify(
        ecc_sig, message, ec.ECDSA(hashes.SHA256())
    )
ecc_verify_wall = time.time() - start_wall
ecc_verify_cpu = time.process_time() - start_cpu

results_verification.append({
    "RSA_verify_wall": rsa_verify_wall,
    "RSA_verify_cpu": rsa_verify_cpu,
    "ECC_verify_wall": ecc_verify_wall,
    "ECC_verify_cpu": ecc_verify_cpu
})

df = pd.DataFrame(results_verification)
print(df)

results_ecdh =[]
start_wall = time.time()
start_cpu = time.process_time()
for _ in range(1000):
    p1 = ec.generate_private_key(ec.SECP256R1())
    p2 = ec.generate_private_key(ec.SECP256R1())
    p1.exchange(ec.ECDH(), p2.public_key())
ecdh_wall = time.time() - start_wall
ecdh_cpu = time.process_time() - start_cpu

results_ecdh.append({
    "ECDH_wall": ecdh_wall,
    "ECDH_cpu": ecdh_cpu
})

df = pd.DataFrame(results_ecdh)
print(df)

