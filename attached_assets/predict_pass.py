
import pandas as pd
import joblib

# Load trained model
model = joblib.load("/home/agrim/Desktop/agrim vs/PBL Compiler Design/models/trained_model.pkl")

# Example: Manually enter new feature vector
# Format: [loop_count, func_calls, instr_count, has_branch, uses_memory, uses_global]
new_features = [2, 1, 38, 1, 1, 0]  
# Predict the optimization level
predicted_pass = model.predict([new_features])[0]

print(f" Predicted best optimization pass: {predicted_pass}")