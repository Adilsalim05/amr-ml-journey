# scripts/parse_fastqc_summary.py
import pandas as pd
import glob
import os

def parse_fastqc_summaries(reports_dir):
    rows = []
    for summary_file in glob.glob(os.path.join(reports_dir, "*_fastqc", "summary.txt")):
        sample = os.path.basename(os.path.dirname(summary_file)).replace("_fastqc", "")
        with open(summary_file) as f:
            for line in f:
                status, check, _ = line.strip().split("\t")
                rows.append({"sample": sample, "check": check, "status": status})
    return pd.DataFrame(rows)

if __name__ == "__main__":
    import sys
    reports_dir = sys.argv[1]
    df = parse_fastqc_summaries(reports_dir)
    pivot = df.pivot(index="sample", columns="check", values="status")
    print(pivot)
    pivot.to_csv("results/fastqc_summary_table.csv")
    print("Saved to results/fastqc_summary_table.csv")

