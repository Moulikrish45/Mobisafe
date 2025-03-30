import numpy as np
import pandas as pd
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib

def load_and_preprocess_data(dataset_path):

    df = pd.read_csv(dataset_path)

    # Debugging: Print actual column names
    print("Dataset Columns:", df.columns.tolist())

    # Standardize column names (Remove spaces, lowercase everything)
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    # Define features and target with new standardized names
    features = ['engine_rpm', 'lub_oil_pressure', 'fuel_pressure', 'coolant_pressure', 'lub_oil_temp', 'coolant_temp']
    target = 'engine_condition'  # 1 = Healthy, 0 = Faulty

    # Check if all required features exist
    missing_features = [col for col in features if col not in df.columns]
    if missing_features:
        raise KeyError(f"Missing columns in dataset: {missing_features}")

    # Fill missing values
    df.fillna(df.mean(numeric_only=True), inplace=True)

    # Select Features and Target
    X = df[features].values
    y = df[target].values

    # Feature Scaling
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Ensure the directory exists before saving scaler
    scaler_path = "../../model_weights/scaler_engine.pkl"
    os.makedirs(os.path.dirname(scaler_path), exist_ok=True)
    joblib.dump(scaler, scaler_path)

    # Reshape for LSTM (samples, timesteps=1, features)
    X_scaled = X_scaled.reshape((X_scaled.shape[0], X_scaled.shape[1], 1))

    # Train-Test Split
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

    return X_train, X_test, y_train, y_test