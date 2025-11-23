import re
import pandas as pd
import sys

def parse_jtr_output(text):
    """
    Extracts JtR metrics from output text and returns a list of dict rows.
    """

    rows = []

    line_re = re.compile(
        r'(?P<cracked>\d+)g\s+'                 # cracked
        r'(?P<runtime>\d+:\d+:\d+:\d+)\s+'     # runtime
        r'(?:DONE\s+)?(?:\([^)]+\)\s+)?'       # optional DONE / timestamp
        r'(?:\d+/\d+\s+)?'                      # optional progress
        r'(?P<g_per_s>[\d\.]+)g/s\s+'          # g/s
        r'(?P<p_per_s>[\d\.]+[KMG]?p/s)\s+'    # p/s
        r'(?P<c_per_s>[\d\.]+[KMG]?[cC]/s)\s+' 
        r'(?P<kc_per_s>[\d\.]+[KMG]?C/s)',  
        re.IGNORECASE
    )

    for line in text.splitlines():
        m = line_re.search(line)
        if m:
            rows.append(m.groupdict())

    return rows


def load_and_parse(filename):
    with open(filename, "r", encoding="utf-8") as f:
        text = f.read()

    rows = parse_jtr_output(text)

    if not rows:
        print("⚠ No JtR metric lines found.")
        return

    df = pd.DataFrame(rows)

    def parse_rate(val):
  
     val = val.strip()
     # Remove all non-digit/non-dot characters except K/M/G
     val = re.sub(r'[^\d\.KMG]', '', val)

     multiplier = 1
     if val.endswith('K'):
         multiplier = 1_000
         val = val[:-1]
     elif val.endswith('M'):
         multiplier = 1_000_000
         val = val[:-1]
     elif val.endswith('G'):
         multiplier = 1_000_000_000
         val = val[:-1]

     return float(val) * multiplier
    df["g_per_s"] = df["g_per_s"].astype(float)
    df["p_per_s"] = df["p_per_s"].map(parse_rate)
    df["c_per_s"] = df["c_per_s"].map(parse_rate)
    df["kc_per_s"] = df["kc_per_s"].map(parse_rate)

    print(df)
    print("\nSummary statistics:\n")
    print(df.describe())


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 parse_jtr.py <jtr_output.txt>")
        sys.exit(1)

    load_and_parse(sys.argv[1])
