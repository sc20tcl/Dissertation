
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


data = pd.read_csv('RequstsPerMinute.csv', parse_dates=['period'], index_col='period')

data['minute_of_day'] = data.index.hour * 60 + data.index.minute 
data['day_of_week'] = data.index.dayofweek 

daily_patterns = data.groupby('minute_of_day')['count'].mean()

weekly_patterns = data.groupby('day_of_week')['count'].mean()

# Plot daily 
plt.figure(figsize=(12, 6))
daily_patterns.plot(title='Average RPM per Minute of Day')
plt.xlabel('Minute of Day')
plt.ylabel('Average RPM')
plt.tight_layout()
plt.savefig('DataSetGraphs/daily_patterns_final.png')

# Plot weekly 
plt.figure(figsize=(12, 6))
weekly_patterns.plot(title='Average RPM per Day of Week')
plt.xlabel('Day of Week')
plt.ylabel('Average RPM')
plt.xticks(np.arange(7), ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'], rotation=45)
plt.tight_layout()
plt.savefig('DataSetGraphs/weekly_patterns_final.png')

# Plot the entire dataset
plt.figure(figsize=(12, 6))
data['count'].plot(title='RPM Over Entire Dataset')
plt.xlabel('Date')
plt.ylabel('RPM')
plt.tight_layout()
plt.savefig('DataSetGraphs/entire_dataset_trend_final.png')

# plot monthly
plt.figure(figsize=(12, 6))
data['count'].resample('M').mean().plot(title='Monthly Average RPM')
plt.xlabel('Month')
plt.ylabel('Average RPM')
plt.tight_layout()
plt.savefig('DataSetGraphs/monthly_trends_final.png')
