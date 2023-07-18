import subprocess
import pytest
import os
import yaml


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
        print("AWS cluster has been created!")

    # def test_create_azure_cluster(self):
    #     print("Running test create cluster in Azure")
    #     os.chdir(os.path.join(os.path.dirname(__file__), '..'))
    #     result = subprocess.run(['python3', 'lab.py', 'create', 'cluster', '--cloud-provider', 'Azure'], capture_output=True, text=True)
    #     print("Azure create cluster result:", result.stdout)
    #     assert result.returncode == 0
    #     print("Azure cluster has been created!")


    # def test_create_gcp_cluster(self):
    #     print("Running test create cluster in GCP")
    #     os.chdir(os.path.join(os.path.dirname(__file__), '..'))
    #     result = subprocess.run(['python3', 'lab.py', 'create', 'cluster', '--cloud-provider', 'GCP'], capture_output=True, text=True)
    #     print("GCP create cluster result:", result.stdout)
    #     assert result.returncode == 0
    #     print("GCP cluster has been created!")
    
    def test_destroy_cluster(self):
        print("Running test destroy cluster")
        os.chdir(os.path.join(os.path.dirname(__file__), '..'))

        # Read cluster details from cluster.yaml
        cluster_yaml_path = os.path.join(os.getcwd(), 'cluster_credentials', 'cluster.yaml')
        assert os.path.isfile(cluster_yaml_path)
        with open(cluster_yaml_path, 'r') as file:
            cluster_data = yaml.safe_load(file)

        # Handle cluster data when it is a list
        if isinstance(cluster_data, list):
            cluster_data = cluster_data[0]

        # Extract cluster name and region
        cluster_name = cluster_data['cluster_name']
        cluster_region = cluster_data['cluster_region']
        print(cluster_name)
        print(cluster_region)
        result = subprocess.run(['python3', 'lab.py', 'destroy', 'cluster', '--name', cluster_name, '--region', cluster_region], capture_output=True, text=True)
        print("Destroy cluster result:", result.stdout)
        print("Destroy cluster error:", result.stderr)
        assert result.returncode == 0
        print("Cluster", cluster_name, "in", cluster_region, "has been destroyed!")

    # def test_nginx_deployment(self):
        # First I need to call the use function in order to setup the kubectl config
        # Then, next to call the add function to create the nginx deployment on the cluster
        # Test it after creation if the nginx is accesible and giving status 200

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


    def test_create_azure_cluster(self):
        print("Running test create cluster in Azure")
        os.chdir(os.path.join(os.path.dirname(__file__), '..'))
        result = subprocess.run(['python3', 'lab.py', 'create', 'cluster', '--cloud-provider', 'Azure'], capture_output=True, text=True)
        print("Azure create cluster result:", result.stdout)
        assert result.returncode == 0

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

    def test_destroy_cluster(self):
        os.chdir(os.path.join(os.path.dirname(__file__), '..'))
        cluster_name = "YOUR_CLUSTER_NAME"
        cluster_region = "YOUR_CLUSTER_REGION"
        result = subprocess.run(['python3', 'lab.py', 'destroy', 'cluster', cluster_name, cluster_region], capture_output=True, text=True)
        assert result.returncode == 0

    # def test_destroy_cluster(self):
    #     os.chdir(os.path.join(os.path.dirname(__file__), '..'))
    #     cluster_name = "YOUR_CLUSTER_NAME"
    #     cluster_region = "YOUR_CLUSTER_REGION"
    #     result = subprocess.run(['python3', 'lab.py', 'destroy', 'cluster', cluster_name, cluster_region], capture_output=True, text=True)
    #     assert result.returncode == 0

if __name__ == '__main__':
    pytest.main()