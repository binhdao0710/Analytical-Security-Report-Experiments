import os
import time
import pandas as pd
import statistics
from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305
import matplotlib.pyplot as plt

RUNS = 5
SIZES = {
    "small": 4 * 1024,
    "medium": 1 * 1024 * 1024,
    "large": 50 * 1024 * 1024,
}

def stats(times):
    return statistics.mean(times), (statistics.stdev(times) if len(times) > 1 else 0)

def time_func(func, *args):
    wall = []
    cpu = []
    for _ in range(RUNS):
        t0 = time.perf_counter()
        c0 = time.process_time()
        func(*args)
        c1 = time.process_time()
        t1 = time.perf_counter()
        wall.append(t1 - t0)
        cpu.append(c1 - c0)
    return stats(wall), stats(cpu)

def aes_encrypt(key, plaintext):
    nonce = os.urandom(12)
    aes = AESGCM(key)
    ct = aes.encrypt(nonce, plaintext, None)
    return nonce + ct

def aes_decrypt(key, blob):
    nonce = blob[:12]
    ct = blob[12:]
    aes = AESGCM(key)
    return aes.decrypt(nonce, ct, None)

def chacha_encrypt(key, plaintext):
    nonce = os.urandom(12)
    cc = ChaCha20Poly1305(key)
    ct = cc.encrypt(nonce, plaintext, None)
    return nonce + ct

def chacha_decrypt(key, blob):
    nonce = blob[:12]
    ct = blob[12:]
    cc = ChaCha20Poly1305(key)
    return cc.decrypt(nonce, ct, None)

def run_bench():
    rows = []
    key_aes = os.urandom(32)
    key_chacha = os.urandom(32)

    for label, size in SIZES.items():
        data = os.urandom(size)
        mb = size / (1024 * 1024)

        # AES Encrypt
        (w_mean, w_std), (c_mean, c_std) = time_func(aes_encrypt, key_aes, data)
        rows.append([label, "AES-GCM encrypt", size, w_mean, c_mean, mb/w_mean])

        # AES Decrypt
        blob = aes_encrypt(key_aes, data)
        (w_mean, w_std), (c_mean, c_std) = time_func(aes_decrypt, key_aes, blob)
        rows.append([label, "AES-GCM decrypt", size, w_mean, c_mean, mb/w_mean])

        # ChaCha Encrypt
        (w_mean, w_std), (c_mean, c_std) = time_func(chacha_encrypt, key_chacha, data)
        rows.append([label, "ChaCha20 encrypt", size, w_mean, c_mean, mb/w_mean])

        # ChaCha Decrypt
        blob = chacha_encrypt(key_chacha, data)
        (w_mean, w_std), (c_mean, c_std) = time_func(chacha_decrypt, key_chacha, blob)
        rows.append([label, "ChaCha20 decrypt", size, w_mean, c_mean, mb/w_mean])

    df = pd.DataFrame(rows, columns=[
        "Size", "Operation", "Bytes", "Wall Time (s)", "CPU Time (s)", "MB/s"
    ])
    df.to_csv("crypto_benchmarks.csv", index=False)
    print(df)
    return df

def plot_results(df):
    plt.figure(figsize=(8,6))

    for op in df["Operation"].unique():
        subset = df[df["Operation"] == op]
        plt.plot(subset["Bytes"], subset["MB/s"], marker='o', label=op)

    plt.xlabel("Plaintext size (bytes)")
    plt.ylabel("Throughput (MB/s)")
    plt.title("Symmetric Encryption Performance")
    plt.legend()
    plt.xscale('log')
    plt.grid(True, which='both', linestyle='--', alpha=0.5)
    plt.show()

if __name__ == "__main__":
    df = run_bench()
    plot_results(df)

