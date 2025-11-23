import time, os, csv, gc
from argon2 import PasswordHasher
import psutil

def hash_once(ph, pw):
    t0 = time.perf_counter()
    ph.hash(pw)
    return time.perf_counter() - t0

def peak_mem_during(fn):
    pid = os.getpid()
    proc = psutil.Process(pid)
    peak = 0
    import threading, time as t

    keep = True
    def poll():
        nonlocal peak, keep
        while keep:
            try:
                rss = proc.memory_info().rss
                if rss > peak:
                    peak = rss
            except psutil.NoSuchProcess:
                break
            t.sleep(0.01)

    th = threading.Thread(target=poll)
    th.start()
    dur = fn()
    keep = False
    th.join()
    return dur, peak

def sweep(out="argon2_avg_by_size.csv"):
    password = "Password123!"

    # Grouped by SIZE category (1, 2, 3)
    categories = {
        1: [
            (1, 65536, 1)
        ],
        2: [
            (2, 131072, 1)
        ],
        3: [
            (3, 262144, 1)
        ]
    }

    # How many times you repeated the WHOLE list (based on your script)
    repetitions = 20

    with open(out, "w", newline='') as f:
        w = csv.writer(f)
        w.writerow(["size_category", "avg_wall_time_s", "avg_peak_rss"])

        for size, param_list in categories.items():

            all_times = []
            all_mem = []

            for _ in range(repetitions):
                for (t_cost, m_cost, par) in param_list:
                    ph = PasswordHasher(time_cost=t_cost, memory_cost=m_cost, parallelism=par)
                    gc.collect()
                    dur, peak = peak_mem_during(lambda: hash_once(ph, password))
                    all_times.append(dur)
                    all_mem.append(peak)

            # compute average for the whole size category
            avg_time = sum(all_times) / len(all_times)
            avg_mem = sum(all_mem) / len(all_mem)

            w.writerow([size, avg_time, avg_mem])
            print(f"Category {size} → avg time={avg_time}, avg rss={avg_mem}")

if __name__ == "__main__":
    sweep()

