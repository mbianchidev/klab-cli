import os
import subprocess
import time
import requests
from kubernetes import client, config


class TestAzureNginx:
    def test_azure_init(self):
        print("Running test_init")
        os.chdir(os.path.join(os.path.dirname(__file__), '..'))
        print("Changed directory to:", os.getcwd())
        result = subprocess.run(['python3', 'lab.py', 'init'], capture_output=True, text=True)
        print("Init result:", result.stdout)
        assert result.returncode == 0

    def test_azure_create_cluster(self):
        print("Running test create cluster in Azure")
        os.chdir(os.path.join(os.path.dirname(__file__), '..'))
        result = subprocess.run(['python3', 'lab.py', 'create', 'cluster', '-pr', 'Azure'], capture_output=True, text=True)
        print("Azure create cluster result:", result.stdout)
        time.sleep(550)
        assert result.returncode == 0
        print("Azure cluster has been created!")

    def test_azure_use_cluster(self):
        print("Running test for use command for cluster in Azure")
        os.chdir(os.path.join(os.path.dirname(__file__), '..'))
        subprocess.run(['python3', 'lab.py', 'use', 'cluster', 'aks', '--provider', 'Azure', '--resource-group', 'kubelab_resource_group'])
        # TODO actually test something here to verify the cluster is up and running
        print("Use for Azure cluster has pass all the test")

    def test_azure_install_nginx_deployment(self):
        print("Running test for add command in Azure")
        os.chdir(os.path.join(os.path.dirname(__file__), '..'))
        result = subprocess.run(['python3', 'lab.py', 'add', 'nginx'], capture_output=True, text=True)
        print("Azure add command result:", result.stdout)
        time.sleep(10)
        config.load_kube_config()

        # Create Kubernetes API client
        api = client.AppsV1Api()
        deployment_name = "nginx"  # TODO this should be parametric
        namespace = "default"  # TODO this should be parametric
        try:
            deployment = api.read_namespaced_deployment(deployment_name, namespace)
        except client.ApiException as e:
            assert False, f"NGINX deployment '{deployment_name}' not found in namespace '{namespace}'"

        print("Deployment found: ", deployment)
        api_core = client.CoreV1Api()

        nginx_service_name = "nginx"  # TODO this should be parametric
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
        time.sleep(10)

    def test_azure_update_nginx_deployment(self):
        print("Running test for update command in Azure")
        os.chdir(os.path.join(os.path.dirname(__file__), '..'))
        result = subprocess.run(['python3', 'lab.py', 'update', 'nginx', '--type=deployment', '--version=latest'], capture_output=True, text=True)
        print("Azure update command result:", result.stdout)
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

    def test_azure_switch_nginx_deployment(self):
        print("Running test for switch to operator command in Azure")
        os.chdir(os.path.join(os.path.dirname(__file__), '..'))
        subprocess.run(['python3', 'lab.py', 'add', 'nginx'])
        time.sleep(10)
        subprocess.run(['kubectl', 'apply', '-f', 'catalog/nginx/nginx_operator_test/nginx-ingress.yaml'])
        time.sleep(10)
        config.load_kube_config()

        # Create Kubernetes API client
        api = client.AppsV1Api()
        deployment_name = "nginxingress-sample-nginx-ingress-controller"  # TODO this should be parametric
        namespace = "default"  # TODO this should be parametric
        try:
            deployment = api.read_namespaced_deployment(deployment_name, namespace)
        except client.ApiException as e:
            assert False, f"NGINX deployment '{deployment_name}' not found in namespace '{namespace}'"

        print("Deployment found: ", deployment)
        api_core = client.CoreV1Api()

        nginx_service_name = "nginx"  # TODO this should be parametric
        try:
            service = api_core.read_namespaced_service(nginx_service_name, namespace)
        except client.ApiException as e:
            assert False, f"NGINX service '{nginx_service_name}' not found in namespace '{namespace}'"

        nginx_test_ip = service.status.load_balancer.ingress[0].ip
        nginx_test_url = f"http://{nginx_test_ip}:/nginx-health"

        try:
            response = requests.get(nginx_test_url)
            assert response.status_code == 200, "NGINX is not accessible with HTTP 200"
            print("NGINX is installed and accessible with HTTP 200", response)
        except requests.exceptions.RequestException as e:
            assert False, f"Error making request to NGINX: {e}"
        time.sleep(10)

    def test_azure_delete_operator(self):
        print("Running test for delete the operator in Azure")
        os.chdir(os.path.join(os.path.dirname(__file__), '..'))
        result = subprocess.run(['python3', 'lab.py', 'delete', 'nginx', '--type=operator'], capture_output=True, text=True)
        print("Azure delete operator result:", result.stdout)
        time.sleep(5)
        assert result.returncode == 0
        print("Successfully deleted the operator")

    def test_azure_destroy_cluster(self):
        print("Running test delete cluster in Azure")
        os.chdir(os.path.join(os.path.dirname(__file__), '..'))
        subprocess.run(['python3', 'lab.py', 'destroy', 'cluster', '--name', 'aks', '--region', 'eastus'])
        # TODO test cluster is not accessible anymore
        print("Azure cluster has been deleted!")
