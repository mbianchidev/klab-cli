import subprocess
import pytest
import os
import time
import requests
from kubernetes import client, config

class TestGCPNginx:
    def test_gcp_init(self):
        print("Running test_init")
        os.chdir(os.path.join(os.path.dirname(__file__), '..'))
        print("Changed directory to:", os.getcwd())
        result = subprocess.run(['python3', 'lab.py', 'init'], capture_output=True, text=True)
        assert result.returncode == 0

    def test_gcp_create_cluster(self):
        print("Running test create cluster in GCP")
        os.chdir(os.path.join(os.path.dirname(__file__), '..'))
        result = subprocess.run(['python3', 'lab.py', 'create', 'cluster', '-pr', 'GCP', '-p', 'cts-project-388707'], capture_output=True, text=True)
        time.sleep(980)
        assert result.returncode == 0
        print("GCP cluster has been created!")

    def test_gcp_use_cluster(self):
        print("Running test for use command for cluster in GCP")
        os.chdir(os.path.join(os.path.dirname(__file__), '..'))
        result = subprocess.run(['python3', 'lab.py', 'use', 'cluster', 'gke', '--provider', 'GCP', '-r', 'europe-central2-a', '-p', 'cts-project-388707'])
        time.sleep(10)
        assert result.returncode == 0
        print("Use for GCP cluster has passed.")

    def test_gcp_install_nginx_deployment(self):
        print("Running test for add command in GCP")
        os.chdir(os.path.join(os.path.dirname(__file__), '..'))
        result = subprocess.run(['python3', 'lab.py', 'add', 'nginx', '--version=1.24.0', '--yes'], capture_output=True, text=True)
        time.sleep(150)
        print("GCP add command result:", result.stdout)
        config.load_kube_config()

        # Create Kubernetes API client
        api = client.AppsV1Api()
        deployment_name = "nginx"
        namespace = "default"
        try:
            deployment = api.read_namespaced_deployment(deployment_name, namespace)
        except client.ApiException as e:
            assert False, f"NGINX deployment '{deployment_name}' not found in namespace '{namespace}'"

        print("Deployment found: ", deployment)
        api_core = client.CoreV1Api()

        nginx_service_name = "nginx"
        try:
            service = api_core.read_namespaced_service(nginx_service_name, namespace)
        except client.ApiException as e:
            assert False, f"NGINX service '{nginx_service_name}' not found in namespace '{namespace}'"

        if service.status.load_balancer and service.status.load_balancer.ingress:
            nginx_test_ip = service.status.load_balancer.ingress[0].ip
            print(nginx_test_ip)
            nginx_test_url = f"http://{nginx_test_ip}:80"
            print(nginx_test_url)

            response = requests.get(nginx_test_url)
            assert response.status_code == 200, "NGINX is not accessible with HTTP 200"
            print("NGINX is installed and accessible with HTTP 200", response)
            time.sleep(10)
        else:
            print("Load balancer information not available yet.")
        
        assert result.returncode == 0

    def test_gcp_update_nginx_deployment(self):
        print("Running test for update command in GCP")
        os.chdir(os.path.join(os.path.dirname(__file__), '..'))
        result = subprocess.run(['python3', 'lab.py', 'update', 'nginx', '--type', 'deployment', '--version', 'latest'], capture_output=True, text=True)
        print("GCP update command result:", result.stdout)
        config.load_kube_config()
        time.sleep(120)

        # Create Kubernetes API client
        api = client.AppsV1Api()
        deployment_name = "nginx"
        namespace = "default"
        try:
            deployment = api.read_namespaced_deployment(deployment_name, namespace)
        except client.ApiException as e:
            assert False, f"NGINX deployment '{deployment_name}' not found in namespace '{namespace}'"

        print("Deployment found: ", deployment)
        api_core = client.CoreV1Api()

        nginx_service_name = "nginx"
        try:
            service = api_core.read_namespaced_service(nginx_service_name, namespace)
        except client.ApiException as e:
            assert False, f"NGINX service '{nginx_service_name}' not found in namespace '{namespace}'"

        nginx_test_ip = service.status.load_balancer.ingress[0].ip
        nginx_test_url = f"http://{nginx_test_ip}:80"

        try:
            response = requests.get(nginx_test_url)
            assert response.status_code == 200, "NGINX is not accessible with HTTP 200"
            print("NGINX is installed and accessible with HTTP 200", response)
        except requests.exceptions.RequestException as e:
            assert False, f"Error making request to NGINX: {e}"
        assert result.returncode == 0
        time.sleep(5)

    def test_gcp_switch_nginx_deployment(self):
        print("Running test for switch to operator command in GCP")
        os.chdir(os.path.join(os.path.dirname(__file__), '..'))
        subprocess.run(['python3', 'lab.py', 'add', 'nginx', '--yes'])
        time.sleep(10)
        subprocess.run(['kubectl', 'apply', '-f', 'catalog/nginx/nginx_operator_test/nginx-ingress.yaml'])
        time.sleep(120)
        config.load_kube_config()

        # Create Kubernetes API client
        api = client.AppsV1Api()
        deployment_name = "nginxingress-sample-nginx-ingress-controller"
        namespace = "default"
        try:
            deployment = api.read_namespaced_deployment(deployment_name, namespace)
        except client.ApiException as e:
            assert False, f"NGINX deployment '{deployment_name}' not found in namespace '{namespace}'"

        print("Deployment found: ", deployment)
        api_core = client.CoreV1Api()

        nginx_service_name = "nginxingress-sample-nginx-ingress-controller"
        try:
            service = api_core.read_namespaced_service(nginx_service_name, namespace)
        except client.ApiException as e:
            assert False, f"NGINX service '{nginx_service_name}' not found in namespace '{namespace}'"

        nginx_test_ip = service.status.load_balancer.ingress[0].ip
        print(nginx_test_ip)
        nginx_test_url = f"http://{nginx_test_ip}/nginx-health"
        print(nginx_test_url)

        try:
            response = requests.get(nginx_test_url)
            assert response.status_code == 200, "NGINX is not accessible with HTTP 200"
            print("NGINX is installed and accessible with HTTP 200", response)
        except requests.exceptions.RequestException as e:
            assert False, f"Error making request to NGINX: {e}"
        time.sleep(10)

    def test_gcp_delete_operator(self):
        print("Running test for delete the operator in GCP")
        os.chdir(os.path.join(os.path.dirname(__file__), '..'))
        result = subprocess.run(['python3', 'lab.py', 'delete', 'nginx', '--type=operator'], capture_output=True, text=True)
        print("AWS delete operator result:", result.stdout)
        time.sleep(15)
        assert result.returncode == 0
        print("Successfully deleted the operator")

    def test_gcp_destroy_cluster(self):
        print("Running destroy cluster in GCP")
        os.chdir(os.path.join(os.path.dirname(__file__), '..'))
        result = subprocess.run(['python3', 'lab.py', 'destroy', 'cluster', '--name', 'gke', '--region', 'europe-central2', '-y'], capture_output=True, text=True)
        assert result.returncode == 0
        print("GCP cluster has been destroyed!")


if __name__ == '__main__':
    pytest.main()
