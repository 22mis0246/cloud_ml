import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import LabelEncoder, StandardScaler
import joblib

# Load dataset
df = pd.read_csv("login_dataset.csv")

# Encode categorical data
le_ip = LabelEncoder()
le_device = LabelEncoder()

df["ip_group_encoded"] = le_ip.fit_transform(df["ip_group"])
df["device_encoded"] = le_device.fit_transform(df["device_type"])

# Select features
X = df[[
    "user_id",
    "login_hour",
    "ip_group_encoded",
    "device_encoded"
]]

# -----------------------
# SCALE FEATURES
# -----------------------
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# -----------------------
# Train Isolation Forest
# -----------------------
model = IsolationForest(
    n_estimators=300,
    contamination=0.25,  # increase sensitivity
    random_state=42
)

model.fit(X_scaled)

# Save everything
joblib.dump(model, "anomaly_model.pkl")
joblib.dump(le_ip, "ip_encoder.pkl")
joblib.dump(le_device, "device_encoder.pkl")
joblib.dump(scaler, "scaler.pkl")

print("Model trained and saved successfully!")