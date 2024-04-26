import subprocess
import requests
import time
import subprocess
import re
import pandas as pd

prometheus_pod_query = 'avg(sum(rate(container_cpu_usage_seconds_total{namespace="default", pod=~"teastore-webui-.*", container!="POD", container!=""}[5m])) by (pod))' 
prometheus_node_query = '100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle", instance="10.224.0.6:9100"}[5m])) * 100)'
prometheus_url = 'http://172.165.58.23'
replica_count = 1

stages = [
    {'vus': 100, 'duration': '240s'},
    {'vus': 250, 'duration': '120s'},
    {'vus': 500, 'duration': '120s'},
    {'vus': 750, 'duration': '120s'},
    {'vus': 1000, 'duration': '120s'},
    {'vus': 1250, 'duration': '120s'},
    {'vus': 1500, 'duration': '120s'},
    {'vus': 1750, 'duration': '120s'},
    {'vus': 2000, 'duration': '120s'},
    {'vus': 2250, 'duration': '120s'}
]

def query_prometheus(query):
    try:
        full_url = f"{prometheus_url}/api/v1/query"
        response = requests.get(full_url, params={'query': query})
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
    except requests.exceptions.RequestException as err:
        print(f"Error querying Prometheus: {err}")
    except ValueError as err:
        print(f"Error parsing JSON response: {err}")


def run_stage(stage):
    test_command = f"k6 run --vus {stage['vus']} --duration {stage['duration']} ./k6Job.js"
    print(f"Running stage: {stage}")
    try:
        result = subprocess.run(test_command, check=True, shell=True, text=True, stdout=subprocess.PIPE)
        output = result.stdout
        
        match = re.search(r"http_req_failed[^:]*: (\d+\.\d+)%", output)
        if match:
            failed_rate = match.group(1)
            print(f"HTTP Requests Failed: {failed_rate}%")
        else:
            print("Failed to find the HTTP request failure rate in the output.")
            failed_rate = 6969
        print('Stage complete, querying Prometheus...')
        prometheus_pod_response = query_prometheus(prometheus_pod_query)
        prometheus_node_response = query_prometheus(prometheus_node_query)
        return prometheus_pod_response['data']['result'][0]['value'][1], prometheus_node_response['data']['result'][0]['value'][1], failed_rate
    except subprocess.CalledProcessError as e:
        print(f'Error running k6 stage: {e}')



def scale_deployment(deployment_name, replicas, namespace="default"):
    try:
        command = ["kubectl", "scale", "deployment", deployment_name, "--replicas={}".format(replicas), "-n", namespace]
    
        subprocess.run(command, check=True)
        print(f"Deployment {deployment_name} scaled to {replicas} replicas in the '{namespace}' namespace.")
    
    except subprocess.CalledProcessError as e:
        print(f"Error scaling deployment: {e}")


def run_test(file_path, replica_array):
    data_array = []
    fail_limit = False
    
    # for _ in range(3):
    for replicas in replica_array:
        print("replicas: ", replicas)
        scale_deployment("teastore-webui", replicas)
        print("5 minute cool down...")
        time.sleep(300)
        for stage in stages:
            pod_response, node_response, failed_rate = run_stage(stage)
            data_array.append([replicas, stage['vus'], pod_response, node_response, failed_rate])
            print("fail rate int: ", float(failed_rate))
            if float(failed_rate) > 5:
                fail_limit = True
                print(f"Failed test: {replicas} replicas {stage} stage")
                print("1 minute cool down...")
                time.sleep(60)
                break
            print("1 minute cool down...")
            time.sleep(60)
        print(data_array)
        # time.sleep(600)


        


    headers = ["replicas", "virtual users", "pod response", "node response", "failed rate"]

    df = pd.DataFrame(data_array, columns=headers)

    

    df.to_csv(file_path, index=False)

    print(f"Data written to {file_path}")

replica_array = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            
file_path = 'pod_model_results.csv'

run_test('pod_model_results13.csv', [1, 2, 3])
time.sleep(600)
run_test('pod_model_results46.csv', [4, 5, 6])
time.sleep(600)
run_test('pod_model_results710.csv', [7, 8, 9, 10])