import os
import subprocess
import time
import requests
from kubernetes import client, config


class TestAzureNginx:
    def testInit(self):
        print("Running test_init")
        os.chdir(os.path.join(os.path.dirname(__file__), '..'))
        print("Changed directory to:", os.getcwd())
        result = subprocess.run(['bash', 'lab', 'init'], capture_output=True, text=True)
        print("Init result:", result.stdout)
        assert result.returncode == 0

    def test_create_azure_cluster(self):
        print("Running test create cluster in Azure")
        os.chdir(os.path.join(os.path.dirname(__file__), '..'))
        result = subprocess.run(['bash', 'lab', 'create', 'cluster', '-pr', 'Azure'], capture_output=True, text=True)
        print("Azure create cluster result:", result.stdout)
        time.sleep(750)
        assert result.returncode == 0
        print("Azure cluster has been created!")

    def test_use_azure_cluster(self):
        print("Running test for use command for cluster in Azure")
        os.chdir(os.path.join(os.path.dirname(__file__), '..'))
        subprocess.run(['bash', 'lab', 'use', 'cluster', 'aks', '--provider', 'Azure', '--resource-group', 'kubelab_resource_group'])
        # print("Use command for azure cluster result:", result.stdout)
        # print(result.stdout)
        # assert result.returncode == 0
        print("Use for Azure cluster has pass all the test")

    def install_NGINX_deployment_Azure(self):
        print("Running test for add command in Azure")
        os.chdir(os.path.join(os.path.dirname(__file__), '..'))
        result = subprocess.run(['bash', 'lab', 'add', 'nginx'], capture_output=True, text=True)
        print("Azure add command result:", result.stdout)
        time.sleep(10)
        config.load_kube_config()

        # Create Kubernetes API client
        api = client.AppsV1Api()
        deployment_name = "nginx"  # Replace with your actual NGINX deployment name
        namespace = "default"  # Replace with the appropriate namespace
        try:
            deployment = api.read_namespaced_deployment(deployment_name, namespace)
        except client.ApiException as e:
            assert False, f"NGINX deployment '{deployment_name}' not found in namespace '{namespace}'"
        # Verify NGINX is accessible
        api_core = client.CoreV1Api()

        nginx_service_name = "nginx"  # Replace with your actual NGINX service name
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

    def update_NGINX_deployment(self):
        print("Running test for update command in Azure")
        os.chdir(os.path.join(os.path.dirname(__file__), '..'))
        result = subprocess.run(['bash', 'lab', 'upadate', 'nginx', '--type=deployment', '--version=latest'], capture_output=True, text=True)
        print("Azure add command result:", result.stdout)