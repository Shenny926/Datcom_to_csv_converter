import pandas as pd
from io import StringIO
import numpy as np

path = "datcomsocool.out"

with open(path, "r", encoding="utf-8", errors="ignore") as f:
    all_lines = f.readlines()

config_options = [
    " DATCOM BODY ALONE CONFIGURATION",
    " WING ALONE CONFIGURATION",
    " VERTICAL TAIL CONFIGURATION",
    " WING-BODY CONFIGURATION",
    " BODY-VERTICAL TAIL CONFIGURATION",
    " WING-BODY-VERTICAL TAIL CONFIGURATION"
]

print("\nAvailable configuration types:")
for i, cfg in enumerate(config_options, start=1):
    print(f" {i}. {cfg}")

while True:
    try:
        choice = int(input("\nSelect configuration type (1–6): "))
        if 1 <= choice <= 6:
            break
        else:
            print("Please enter a valid number (1–6).")
    except ValueError:
        print("Invalid input — enter a numeric value.")

selected_config = config_options[choice - 1]
print(f"\nYou selected: {selected_config}")


# Find all lines containing the selected configuration text
config_indices = [
    i for i, line in enumerate(all_lines)
    if selected_config in line
]

if not config_indices:
    raise ValueError(f"No configuration lines found for: {selected_config}")

# Keep only the first TWO valid configuration occurrences
config_indices = config_indices[:2]

print(f"\nConfiguration '{selected_config}' found at lines: {config_indices}")

# For each config index, search downward until the first ALPHA line
alpha_indices = []

for cfg_idx in config_indices:
    for j in range(cfg_idx + 1, len(all_lines)):
        if " ALPHA " in all_lines[j]:
            alpha_indices.append(j)
            break   # important: stop after the FIRST ALPHA below this config block

if not alpha_indices:
    raise ValueError("No ALPHA tables found after selected configuration.")

print("Detected ALPHA table starts at lines:", alpha_indices)


dataframes = []

for m in alpha_indices:
    start = m
    dataheight = 2
    while True:
        idx = m + dataheight
        if idx >= len(all_lines):
            break
        line = all_lines[idx].strip()
        if not line:
            break
        parts = line.split()
        if not parts:
            break
        first = parts[0]
        if first in ("0", "1"):
            break
        try:
            float(first)
        except ValueError:
            break
        dataheight += 1

    end = m + dataheight

    block_lines = all_lines[start:end]


    buf = StringIO("".join(line[1:] for line in block_lines))

    df = pd.read_fwf(
        buf,
        header=0,
        skiprows=[1],
        infer_nrows=200,
        dtype=str
    )

    # Normalize to 12 columns
    if df.shape[1] > 12:
        df = df.iloc[:, :12]
    elif df.shape[1] < 12:
        for i in range(df.shape[1], 12):
            df[f"col_{i+1}"] = np.nan

    # Replace empty/whitespace with NA
    df = df.replace(r'^\s*$', pd.NA, regex=True)

    dataframes.append(df)

final_df = pd.concat(dataframes, ignore_index=True)


output_path = f"{selected_config.replace(' ', '_')}.csv"
final_df.to_csv(output_path, index=False)

print("\n----------------------------------------")
print("Processing complete.")
print("Combined rows:", final_df.shape[0])
print(f"CSV saved as: {output_path}")
print("----------------------------------------")


