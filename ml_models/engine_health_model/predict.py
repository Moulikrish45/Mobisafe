import numpy as np
import joblib
from keras import models

lstm_model = models.load_model("ml_models/model_weights/lstm_engine.h5")
scaler = joblib.load("ml_models/model_weights/scaler_engine.pkl")

def predict_engine_health(engine_rpm, lub_oil_pressure, fuel_pressure, coolant_pressure, lub_oil_temp, coolant_temp):
    input_features = np.array([engine_rpm, lub_oil_pressure, fuel_pressure, coolant_pressure,lub_oil_temp, coolant_temp])

    input_scaled = scaler.transform(input_features.reshape(1, -1))

    lstm_prediction = lstm_model.predict(input_scaled)[0][0]

    engine_condition = 1 if lstm_prediction > 0.5 else 0

    return {
        "lstm_prediction": float(lstm_prediction),
        "engine_condition": engine_condition
    }
