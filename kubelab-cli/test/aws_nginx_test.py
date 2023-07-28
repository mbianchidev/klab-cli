import subprocess
import pytest
import os
import requests
from kubernetes import client, config

class TestAWSNginx:
    def test_init(self):
        print("Running test_init")
        os.chdir(os.path.join(os.path.dirname(__file__), '..'))
        print("Changed directory to:", os.getcwd())
        result = subprocess.run(['python3', 'lab.py', 'init'], capture_output=True, text=True)
        print("Init result:", result.stdout)
        assert result.returncode == 0

    def test_create_aws_cluster(self):
        print("Running test create cluster in AWS")
        os.chdir(os.path.join(os.path.dirname(__file__), '..'))
        result = subprocess.run(['python3', 'lab.py', 'create', 'cluster', '-cn', 'eks', '-pr' 'AWS', '-r', 'eu-west-2'], capture_output=True, text=True)
        print("AWS create cluster result:", result.stdout)
        assert result.returncode == 0
        print("AWS cluster has been created!")

    def test_install_nginx_deployment(self):
        os.chdir(os.path.join(os.path.dirname(__file__), '..'))
        subprocess.run(['python3', 'lab.py', 'use', 'cluster', 'eks', '--provider', 'aws', '--region', 'us-west-2'])
        subprocess.run(['python3', 'lab.py', 'add', 'deployment', 'nginx', '--version', '1.4.5'])

        # Load Kubernetes configuration
        config.load_kube_config()

        # Create Kubernetes API client
        api = client.CoreV1Api()

        # Verify NGINX deployment
        deployment_name = "nginx-deployment"  # Replace with your actual NGINX deployment name
        namespace = "default"  # Replace with the appropriate namespace
        try:
            deployment = api.read_namespaced_deployment(deployment_name, namespace)
        except client.ApiException as e:
            assert False, f"NGINX deployment '{deployment_name}' not found in namespace '{namespace}'"

        # Verify NGINX version (Assuming NGINX version is available in deployment annotations or labels)
        # Example: assert deployment.metadata.annotations.get('nginx.version') == '1.4.5', "Incorrect NGINX version installed"

        # Verify NGINX is accessible
        nginx_service_name = "nginx-service"  # Replace with your actual NGINX service name
        try:
            service = api.read_namespaced_service(nginx_service_name, namespace)
        except client.ApiException as e:
            assert False, f"NGINX service '{nginx_service_name}' not found in namespace '{namespace}'"

        # Temporary NGINX URL for testing (assuming the service is of type LoadBalancer)
        nginx_test_url = f"http://{service.status.load_balancer.ingress[0].hostname}:80"

        # Verify NGINX accessibility
        response = requests.get(nginx_test_url)
        assert response.status_code == 200, "NGINX is not accessible with HTTP 200"


if __name__ == '__main__':
    pytest.main()
