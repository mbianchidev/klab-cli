import subprocess
import pytest
import os

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
        result = subprocess.run(['python3', 'lab.py', 'create', 'cluster', '--cloud-provider', 'AWS'], capture_output=True, text=True)
        print("AWS create cluster result:", result.stdout)
        assert result.returncode == 0

    # def test_create_azure_cluster(self):
    #     print("Running test create cluster in Azure")
    #     os.chdir(os.path.join(os.path.dirname(__file__), '..'))
    #     result = subprocess.run(['python3', 'lab.py', 'create', 'cluster', '--cloud-provider', 'Azure'], capture_output=True, text=True)
    #     print("Azure create cluster result:", result.stdout)
    #     assert result.returncode == 0

    # def test_create_gcp_cluster(self):
    #     print("Running test create cluster in GCP")
    #     os.chdir(os.path.join(os.path.dirname(__file__), '..'))
    #     result = subprocess.run(['python3', 'lab.py', 'create', 'cluster', '--cloud-provider', 'GCP'], capture_output=True, text=True)
    #     print("GCP create cluster result:", result.stdout)
    #     assert result.returncode == 0

    # def test_nginx_deployment(self):
    #     os.chdir(os.path.join(os.path.dirname(__file__), '..'))
    #     result = subprocess.run(['python3', 'lab.py', 'add', 'deployment', 'nginx'], capture_output=True, text=True)
    #     assert result.returncode == 0

    # def test_catalog_yaml(self):
    #     os.chdir(os.path.join(os.path.dirname(__file__), '../catalog'))
    #     catalog_path = os.path.join(os.getcwd(), 'catalog.yaml')
    #     assert os.path.isfile(catalog_path)
    #     with open(catalog_path, 'r') as file:
    #         catalog = file.read()
    #         assert 'nginx' in catalog

    # def test_update_nginx_version(self):
    #     os.chdir(os.path.join(os.path.dirname(__file__), '..'))
    #     result = subprocess.run(['python3', 'lab.py', 'update', '--type', 'deployment', 'nginx'], capture_output=True, text=True)
    #     assert result.returncode == 0

    # def test_switch_to_operator(self):
    #     os.chdir(os.path.join(os.path.dirname(__file__), '..'))
    #     result = subprocess.run(['python3', 'lab.py', 'update', '--type', 'operator', 'nginx'], capture_output=True, text=True)
    #     assert result.returncode == 0

    # def test_remove_operator_installation(self):
    #     os.chdir(os.path.join(os.path.dirname(__file__), '..'))
    #     result = subprocess.run(['python3', 'lab.py', 'delete', '--type', 'operator', 'nginx'], capture_output=True, text=True)
    #     assert result.returncode == 0

    # def test_destroy_cluster(self):
    #     os.chdir(os.path.join(os.path.dirname(__file__), '..'))
    #     cluster_name = "YOUR_CLUSTER_NAME"
    #     cluster_region = "YOUR_CLUSTER_REGION"
    #     result = subprocess.run(['python3', 'lab.py', 'destroy', 'cluster', cluster_name, cluster_region], capture_output=True, text=True)
    #     assert result.returncode == 0

if __name__ == '__main__':
    pytest.main()