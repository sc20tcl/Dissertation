import math
import requests
from kubernetes import client, config

def query_prometheus():
    prometheus_url = 'http://prometheus-server.default.svc.cluster.local/api/v1/query'
    query = 'sum(rate(http_requests_total{app="teastore_webui"}[1m])) by (app)'
    
    response = requests.get(prometheus_url, params={'query': query})
    results = response.json()['data']['result']
    
    if results:
        requests_per_minute = float(results[0]['value'][1])
        return requests_per_minute
    else:
        return 0

def calculate_desired_pods(requests_per_minute):
    return math.ceil(requests_per_minute / 1000)

def scale_deployment(num_pods):
    config.load_kube_config()
    k8s_client = client.AppsV1Api()
    
    deployment_name = 'teastore_webui'
    namespace = 'default'
    
    k8s_client.patch_namespaced_deployment_scale(
        name=deployment_name,
        namespace=namespace,
        body={'spec': {'replicas': num_pods}}
    )

def main():
    requests_per_minute = query_prometheus()

    num_pods = calculate_desired_pods(requests_per_minute)

    scale_deployment(num_pods)
    print(f"Deployment scaled to {num_pods} pods based on {requests_per_minute} requests per minute.")

if __name__ == "__main__":
    main()
