import subprocess
import requests
import time
import pandas as pd

# Prometheus configurations
prometheus_url = 'http://172.165.58.23'
prometheus_pod_query = 'avg(sum(rate(container_cpu_usage_seconds_total{namespace="default", pod=~"teastore-webui-.*", container!="POD", container!=""}[5m])) by (pod))'
prometheus_node_query = '100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle", instance="10.224.0.6:9100"}[5m])) * 100)'
pod_count_query = 'count(kube_pod_info{namespace="default", pod=~"teastore-webui-.*"}) by (namespace)'
last_minute_query = 'sum(rate(http_requests_total[1m]))'

def query_prometheus(query):
    """Query Prometheus using the HTTP API and return the JSON response."""
    try:
        full_url = f"{prometheus_url}/api/v1/query"
        response = requests.get(full_url, params={'query': query})
        response.raise_for_status()
        data = response.json()
        return data['data']['result']
    except requests.exceptions.RequestException as err:
        print(f"Error querying Prometheus: {err}")
        return None

def run_stage(stage):
    """Run a k6 test stage."""
    test_command = f"k6 run --vus {stage['vus']} --duration {stage['duration']} ./k6Job.js"
    print(f"Running stage with {stage['vus']} virtual users for {stage['duration']}.")
    try:
        result = subprocess.run(test_command, check=True, shell=True, text=True, stdout=subprocess.PIPE)
        output = result.stdout
        print(output)  # Output the k6 run results
        last_minute_requests = query_prometheus(last_minute_query)
        pod_count_result = query_prometheus(pod_count_query)
        if last_minute_requests:
            requests_count = last_minute_requests[0]['value'][1]
        else:
            requests_count = 'RPM Query failed'
        if pod_count_result:
            pod_count = pod_count_result[0]['value'][1]
        else:
            pod_count = 'Pod Query failed'
        return requests_count, pod_count
    except subprocess.CalledProcessError as e:
        print(f'Error running k6 stage: {e}')
        return 'Test failed'


data = pd.read_csv("../ValidateData.csv", parse_dates=['period'], index_col='period')

data = data['1998-06-24 13:49:00': '1998-06-24 14:49:00']

test_data = []
for period, row in data.iterrows():
    stage = {'vus': int(row['count']/60), 'duration': '60s'}  # Run each stage for 1 minute
    print(f"Scheduling test for {stage['vus']} virtual users at {period}.")
    requests_count, pod_count = run_stage(stage)
    print(pod_count)
    print(requests_count)
    test_data.append([requests_count, pod_count])

results_df = pd.DataFrame(test_data, columns=['Requests Last Minute', 'Pod Count'])
results_df.to_csv('test_results.csv', index=False)
print("Test results saved to 'test_results.csv'.")
