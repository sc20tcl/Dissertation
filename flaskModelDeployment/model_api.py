from flask import Flask, request, jsonify
import numpy as np
from tensorflow.keras.models import load_model
from joblib import load

app = Flask(__name__)

model = load_model('lstm_model.h5')
scaler = load('scaler.joblib')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    current_sequence = np.array(data['sequence']).reshape(-1, 1)

    current_sequence_scaled = scaler.transform(current_sequence)

    input_sequence = current_sequence_scaled.reshape((1, 15, 1))

    predicted_rpm_scaled = model.predict(input_sequence)
    
    predicted_rpm = scaler.inverse_transform(predicted_rpm_scaled)

    return jsonify({'forecast': predicted_rpm.flatten().tolist()})

if __name__ == '__main__':
    app.run(debug=True)
