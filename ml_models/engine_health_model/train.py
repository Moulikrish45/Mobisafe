from data_preprocessing import load_and_preprocess_data
from model_lstm import create_lstm_model

X_train, X_test, y_train, y_test = load_and_preprocess_data('../datasets/engine_dataset.csv')

model = create_lstm_model(input_shape=(X_train.shape[1], 1))

model.fit(X_train, y_train, epochs=20,batch_size=32,validation_data=(X_test, y_test))

model.save("ml_models/model_weights/lstm_engine.h5")

print("trained model saved")