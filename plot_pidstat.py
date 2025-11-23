import pandas as pd
import matplotlib.pyplot as plt
import sys

def time_to_seconds(timestr):
    h, m, s = map(int, timestr.split(":"))
    return h*3600 + m*60 + s

pidstat_file = sys.argv[1] if len(sys.argv) > 1 else "pidstat_combined.txt"

cpu_data = []
mem_data = []
current_table = None
first_timestamp = None  # for relative timing

with open(pidstat_file, "r") as f:
    for line in f:
        parts = line.split()
        if not parts:
            continue
        
        # Detect table header
        if len(parts) > 1 and parts[1] == "UID":
            if "%CPU" in parts:
                current_table = "cpu"
            elif "%MEM" in parts:
                current_table = "mem"
            continue
        
        if parts[0] in ("Linux", "#"):
            continue

        try:
            timestamp = time_to_seconds(parts[0])
            if first_timestamp is None:
                first_timestamp = timestamp  # record first timestamp
            rel_time = timestamp - first_timestamp  # relative timestamp 0 -> N s
            
            pid = int(parts[2])
            
            if current_table == "cpu":
                cpu = float(parts[7])
                cpu_data.append({"Time": rel_time, "PID": pid, "CPU": cpu})
            elif current_table == "mem":
                mem = float(parts[7])
                mem_data.append({"Time": rel_time, "PID": pid, "MEM": mem})
        except (ValueError, IndexError):
            continue

# Convert to DataFrames
df_cpu = pd.DataFrame(cpu_data)
df_mem = pd.DataFrame(mem_data)

print(df_cpu.head())
print(df_cpu.columns)
print(df_mem.head())
print(df_mem.columns)

# Merge CPU and MEM on Time + PID
df = pd.merge(df_cpu, df_mem, on=["Time", "PID"], how="outer")
df.sort_values("Time", inplace=True)

# Plot
fig, ax1 = plt.subplots(figsize=(10,5))

ax1.set_xlabel("Time (s)")
ax1.set_ylabel("CPU %", color="tab:blue")
ax1.plot(df["Time"], df["CPU"], color="tab:blue", label="CPU %")
ax1.tick_params(axis="y", labelcolor="tab:blue")

ax2 = ax1.twinx()
ax2.set_ylabel("Memory %", color="tab:red") 
ax2.plot(df["Time"], df["MEM"], color="tab:red", label="MEM %") 
ax2.tick_params(axis="y", labelcolor="tab:red")

plt.title("Process CPU and Memory Usage Over Time")
fig.tight_layout()
plt.show()

