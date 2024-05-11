import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error
from math import sqrt

original_data = pd.read_csv('../ValidateData.csv', parse_dates=True, index_col='period')
predicted_data = pd.read_csv('lstm_predictions.csv', parse_dates=True, index_col='period')

def create_graph(start_date, end_date, graph_name):  

    original_filtered = original_data[start_date:end_date]
    predicted_filtered = predicted_data[start_date:end_date]
    rmse = sqrt(mean_squared_error(original_filtered, predicted_filtered))/len(predicted_data)
    print("rsme: ", rmse)

    plt.figure(figsize=(10, 5))
    plt.plot(original_filtered, label='Original Data', linestyle='-', color='blue')
    plt.plot(predicted_filtered, label='Predicted Data', linestyle='--', color='orange')

    plt.title('Comparison of Original and Predicted Data')
    plt.xlabel('Date')
    plt.ylabel('Value')

    plt.legend()

    plt.savefig(f'Model Graphs/{graph_name}.png')


highlight_ranges = [
    ('1998-06-24 16:02:00', '1998-06-24 17:02:00', 'Largest Decrease'), # highest decrease
    ('1998-06-24 13:49:00', '1998-06-24 14:49:00', 'Largest Increase'), # highest increase
    ('1998-06-24 10:24:00', '1998-06-24 11:24:00', "Lowest Variance"), # lowest variance
    ('1998-06-24 16:52:00', '1998-06-24 17:52:00', "Highest Variance") # highest variance

]

for test in highlight_ranges:
    create_graph(test[0], test[1], test[2])