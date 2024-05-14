import requests
import logging
from kubernetes import client, config
import math

def get_traffic(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  
        data = response.json()
        traffic = data.get('traffic', 0)  
        logging.info(f"Successfully called {url}: {response.text}")
        return traffic
    except requests.exceptions.RequestException as e:
        logging.error(f"Error calling {url}: {str(e)}")
        return None
    
def predict_traffic(url, requests_per_minute):
    url = 'http://20.33.62.78:5000/predict'
    
    headers = {'Content-Type': 'application/json'}
    
    data = {
        'current_traffic': requests_per_minute
    }
    
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        json_response = response.json()
        forecast_value = float(json_response['forecast'][0])
        logging.info(f"Successfully called {url}: {response.text}")
        return forecast_value
    else:
        logging.error(f"Failed to get prediction, status code: {response.status_code}")
        return None
    
def optimum_pods(qpm):
    url = "http://20.33.62.78:5002/optimum_pods?qps=" + str(float(qpm)/60)
    response = requests.get(url)
    
    if response.status_code == 200:
        json_response = response.json()
        optimum_pods = int(json_response['optimum_pods'])
        logging.info(f"Successfully called {url}: {response.text}")
        return optimum_pods
    else:
        print(f"Error: Received status code {response.status_code}")
        return None

def scale_deployment(num_pods):
    deployment_name = 'teastore-webui'
    namespace = 'default'
    logging.info(f"Attempting to scale Deployment: {deployment_name} to {num_pods} pods...")
    try:
        config.load_incluster_config()
        k8s_client = client.AppsV1Api()
        
        k8s_client.patch_namespaced_deployment_scale(
            name=deployment_name,
            namespace=namespace,
            body={'spec': {'replicas': num_pods}}
        )
        logging.info(f"Deployment {deployment_name} scaled to {num_pods} pods.")
    except Exception as e:
        logging.error(f"Failed to scale deployment: {str(e)}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    traffic_url = 'http://20.33.62.78:5001/traffic'
    traffic_model_url = 'http://20.33.62.78:5000/predict'

    traffic = get_traffic(traffic_url)
    if traffic is not None:
        predicted_traffic = predict_traffic(traffic_model_url, traffic)
        if predicted_traffic is not None:
            num_pods = optimum_pods(predicted_traffic)
            
            scale_deployment(num_pods)
