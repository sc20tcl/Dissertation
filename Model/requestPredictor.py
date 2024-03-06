import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import load_model
import numpy as np
from joblib import load

# Load the dataset
data_path = '../RequstsPerMinute.csv'  
data = pd.read_csv(data_path, parse_dates=['period'])

# Specified start and stop timestamps
start_timestamp = pd.to_datetime('1998-07-11 11:30:00')
stop_timestamp = pd.to_datetime('1998-07-11 11:50:00')
filtered_data = data[(data['period'] >= start_timestamp) & (data['period'] <= stop_timestamp)]


model = load_model('lstm_model.h5')
scaler = load('scaler.joblib')

def simulate_real_time_prediction_with_timestamps(filtered_data, model, scaler, look_back=10):
    
    for index in range(len(filtered_data) - look_back):
        # Prepare the sequence for prediction
        current_sequence = filtered_data['count'].iloc[index:index+look_back].values.reshape(-1, 1)
        current_sequence_scaled = scaler.transform(current_sequence)
        
        # Make prediction
        input_sequence = current_sequence_scaled.reshape((1, look_back, 1))
        predicted_rpm_scaled = model.predict(input_sequence)
        predicted_rpm = scaler.inverse_transform(predicted_rpm_scaled)
        
        print(f"Predicted RPM at {filtered_data['period'].iloc[index + look_back]}: {predicted_rpm[0][0]}")
        

simulate_real_time_prediction_with_timestamps(filtered_data, model, scaler, look_back=10)