import os
import csv
import re
import pandas as pd

# Paths
ir_dir = "/home/agrim/Desktop/agrim vs/PBL Compiler Design/dataset/code/irs"
os.makedirs(ir_dir, exist_ok=True)
csv_output_path = "/home/agrim/Desktop/agrim vs/PBL Compiler Design/dataset/features.csv"

# Column headers
header = ["code_name", "loop_count", "func_calls", "instr_count", "has_branch", "uses_memory", "uses_global", "best_opt_level"]

# Feature extraction function
def extract_features_from_ir(ir_text):
    loop_count = len(re.findall(r'br label %', ir_text))  # crude loop indicator
    func_calls = len(re.findall(r'call ', ir_text))
    instr_count = len(re.findall(r'^\s*\S+', ir_text, flags=re.MULTILINE))
    has_branch = 1 if re.search(r'br i1|switch', ir_text) else 0
    uses_memory = 1 if re.search(r'(alloca|load|store)', ir_text) else 0
    uses_global = 1 if re.search(r'@', ir_text) else 0
    return loop_count, func_calls, instr_count, has_branch, uses_memory, uses_global

# Extract features from .ll files
feature_rows = []
for file in os.listdir(ir_dir):
    if file.endswith(".ll"):
        with open(os.path.join(ir_dir, file), "r") as f:
            ir_code = f.read()
            features = extract_features_from_ir(ir_code)
            # Dummy default label (can edit manually later)
            feature_rows.append([file] + list(features) + ["O1"])

# Load existing features.csv
if os.path.exists(csv_output_path):
    df_existing = pd.read_csv(csv_output_path)
else:
    df_existing = pd.DataFrame(columns=header)

# Remove old rows of same files
incoming_names = [row[0] for row in feature_rows]
df_existing = df_existing[~df_existing["code_name"].isin(incoming_names)]

# Add new rows
df_new = pd.DataFrame(feature_rows, columns=header)
df_final = pd.concat([df_existing, df_new], ignore_index=True)

# Fix: Ensure best_opt_level is string format "O1", "O2", etc.
df_final["best_opt_level"] = df_final["best_opt_level"].astype(str)
df_final["best_opt_level"] = df_final["best_opt_level"].apply(
    lambda x: f"O{x}" if not str(x).startswith("O") else str(x))

# Save
df_final.to_csv(csv_output_path, index=False)
print("✅ features.csv updated successfully.")