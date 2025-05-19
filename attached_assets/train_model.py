import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib

# Load extracted features
df = pd.read_csv("/home/agrim/Desktop/agrim vs/PBL Compiler Design/dataset/code/features.csv")

# Features and labels
X = df[["loop_count", "func_calls", "instr_count", "has_branch", "uses_memory", "uses_global"]]
y = df["best_opt_level"]

#Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Check if model already exists
model_path = "/home/agrim/Desktop/agrim vs/PBL Compiler Design/models/trained_model.pkl"
if os.path.exists(model_path):
    print(" trained_model.pkl already exists. Skipping training.")
else:
    #  Train and Save model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    joblib.dump(model, model_path)
    print("Model trained and saved as trained_model.pkl")