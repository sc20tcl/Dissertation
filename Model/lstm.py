import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.optimizers import Adam

# Load and preprocess data with date range filtering
def load_and_preprocess_data(filepath, train_start_date, train_end_date, test_start_date, test_end_date):
    data = pd.read_csv(filepath, parse_dates=['period'], index_col='period')
    train_data = data[train_start_date:train_end_date]
    test_data = data[test_start_date:test_end_date]
    
    scaler = MinMaxScaler(feature_range=(0, 1))
    train_scaled = scaler.fit_transform(train_data['count'].values.reshape(-1, 1))
    test_scaled = scaler.transform(test_data['count'].values.reshape(-1, 1))
    
    return train_scaled, test_scaled, scaler

# Function to create dataset for LSTM
def create_dataset(data, look_back=1):
    X, Y = [], []
    for i in range(len(data)-look_back-1):
        a = data[i:(i+look_back), 0]
        X.append(a)
        Y.append(data[i + look_back, 0])
    return np.array(X), np.array(Y)

# Define the LSTM model
def build_model(look_back):
    model = Sequential()
    model.add(LSTM(50, input_shape=(look_back, 1)))
    model.add(Dense(1))
    model.compile(optimizer=Adam(), loss='mean_squared_error')
    return model

def train_and_test_model(model, X_train, y_train, X_test, y_test):
    model.fit(X_train, y_train, epochs=20, batch_size=32)
    test_loss = model.evaluate(X_test, y_test)
    print(f'Test loss: {test_loss}')

# Main processing function
def process_file(filepath, train_start_date, train_end_date, test_start_date, test_end_date, look_back=10):
    train_scaled, test_scaled, scaler = load_and_preprocess_data(filepath, train_start_date, train_end_date, test_start_date, test_end_date)
    
    # Prepare datasets
    X_train, y_train = create_dataset(train_scaled, look_back)
    X_test, y_test = create_dataset(test_scaled, look_back)
    
    # Reshape input for LSTM
    X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))
    X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))
    
    # Build and train model
    model = build_model(look_back)
    train_and_test_model(model, X_train, y_train, X_test, y_test)

# Define your date ranges for training and testing
train_start_date = '1998-04-30 21:30:00'
train_end_date = '1998-05-30 21:30:00'  
test_start_date = '1998-05-31 21:30:00' 
test_end_date = '1998-06-30 21:30:00'    

filepath = '/mnt/data/RequstsPerMinute.csv'
process_file(filepath, train_start_date, train_end_date, test_start_date, test_end_date)