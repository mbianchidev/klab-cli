import subprocess
import pytest
import os
import time
import requests
from kubernetes import client, config

class TestAWSNginx:
    def test_aws_init(self):
        print("Running test_init")
        os.chdir(os.path.join(os.path.dirname(__file__), '..'))
        print("Changed directory to:", os.getcwd())
        result = subprocess.run(['python3', 'lab.py', 'init'], capture_output=True, text=True)
        assert result.returncode == 0

    def test_aws_create_cluster(self):
        print("Running test create cluster in AWS")
        os.chdir(os.path.join(os.path.dirname(__file__), '..'))
        result = subprocess.run(['python3', 'lab.py', 'create', 'cluster', '-pr', 'AWS'], capture_output=True, text=True)
        time.sleep(700)
        assert result.returncode == 0
        print("AWS cluster has been created!")

    def test_aws_use_cluster(self):
        print("Running test for use command for cluster in AWS")
        os.chdir(os.path.join(os.path.dirname(__file__), '..'))
        result = subprocess.run(['python3', 'lab.py', 'use', 'cluster', 'eks', '--provider', 'AWS', '-r', 'eu-west-2'])
        time.sleep(10)
        assert result.returncode == 0
        print("Use for AWS cluster has passed.")

    def test_aws_install_nginx_deployment(self):
        print("Running test for add command in AWS")
        os.chdir(os.path.join(os.path.dirname(__file__), '..'))
        result = subprocess.run(['python3', 'lab.py', 'add', 'nginx', '--version=1.24.0'], capture_output=True, text=True)
        time.sleep(90)
        print("AWS add command result:", result.stdout)
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

        nginx_test_ip = service.status.load_balancer.ingress[0].hostname
        print(nginx_test_ip)
        nginx_test_url = f"http://{nginx_test_ip}:80"
        print(nginx_test_url)

        response = requests.get(nginx_test_url)
        assert response.status_code == 200, "NGINX is not accessible with HTTP 200"
        print("NGINX is installed and accessible with HTTP 200", response)
        time.sleep(10)
        assert result.returncode == 0

    def test_aws_update_nginx_deployment(self):
        print("Running test for update command in AWS")
        os.chdir(os.path.join(os.path.dirname(__file__), '..'))
        result = subprocess.run(['python3', 'lab.py', 'update', 'nginx', '--type=deployment', '--version=latest'], capture_output=True, text=True)
        print("AWS update command result:", result.stdout)
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

        nginx_test_ip = service.status.load_balancer.ingress[0].hostname
        nginx_test_url = f"http://{nginx_test_ip}:80"

        try:
            response = requests.get(nginx_test_url)
            assert response.status_code == 200, "NGINX is not accessible with HTTP 200"
            print("NGINX is installed and accessible with HTTP 200", response)
        except requests.exceptions.RequestException as e:
            assert False, f"Error making request to NGINX: {e}"
        assert result.returncode == 0
        time.sleep(5)

    def test_aws_switch_nginx_deployment(self):
        print("Running test for switch to operator command in AWS")
        os.chdir(os.path.join(os.path.dirname(__file__), '..'))
        subprocess.run(['python3', 'lab.py', 'add', 'nginx'])
        time.sleep(10)
        subprocess.run(['kubectl', 'apply', '-f', 'catalog/nginx/nginx_operator_test/nginx-ingress.yaml'])
        time.sleep(90)
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

        nginx_service_name = "nginx"
        try:
            service = api_core.read_namespaced_service(nginx_service_name, namespace)
        except client.ApiException as e:
            assert False, f"NGINX service '{nginx_service_name}' not found in namespace '{namespace}'"

        nginx_test_ip = service.status.load_balancer.ingress[0].hostname
        nginx_test_url = f"http://{nginx_test_ip}:/nginx-health"

        try:
            response = requests.get(nginx_test_url)
            assert response.status_code == 200, "NGINX is not accessible with HTTP 200"
            print("NGINX is installed and accessible with HTTP 200", response)
        except requests.exceptions.RequestException as e:
            assert False, f"Error making request to NGINX: {e}"
        time.sleep(10)

    def test_aws_delete_operator(self):
        print("Running test for delete the operator in AWS")
        os.chdir(os.path.join(os.path.dirname(__file__), '..'))
        result = subprocess.run(['python3', 'lab.py', 'delete', 'nginx', '--type=operator'], capture_output=True, text=True)
        print("AWS delete operator result:", result.stdout)
        time.sleep(5)
        assert result.returncode == 0
        print("Successfully deleted the operator")

    def test_aws_destroy_cluster(self):
        print("Running destroy cluster in AWS")
        os.chdir(os.path.join(os.path.dirname(__file__), '..'))
        result = subprocess.run(['python3', 'lab.py', 'destroy', 'cluster', '--name', 'eks', '--region', 'eu-west-2', '-y'], capture_output=True, text=True)
        assert result.returncode == 0
        print("AWS cluster has been destroyed!")


if __name__ == '__main__':
    pytest.main()
