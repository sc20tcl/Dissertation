from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)

# Load CSV data into DataFrame
data = pd.read_csv("ValidateData.csv", parse_dates=['period'], index_col='period')

@app.route('/traffic', methods=['GET'])
def get_traffic():
    # Retrieve timestamp from the query parameter
    timestamp = request.args.get('timestamp')
    if not timestamp:
        return jsonify({'error': 'Missing timestamp'}), 400

    try:
        # Convert string timestamp to datetime
        datetime_index = pd.to_datetime(timestamp)
        result = data.loc[datetime_index]
        return jsonify({'traffic': result['count'].item()}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
