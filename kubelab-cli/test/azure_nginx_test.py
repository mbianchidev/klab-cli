import os
import subprocess


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
        result = subprocess.run(['bash', 'lab', 'create', 'cluster', '-pr', 'Azure', '-cn', 'test-Azure', '-rg', 'kubelab-testing', '-r', 'eastus'], capture_output=True, text=True)
        print("Azure create cluster result:", result.stdout)
        assert result.returncode == 0
        print("Azure cluster has been created!")
    
    def test_use_azure_cluster(self):
        print("Running test use for cluster in Azure")
        os.chdir(os.path.join(os.path.dirname(__file__), '..'))
        result = subprocess.run(['bash', 'lab', 'use', 'cluster', 'Test-Azure', '--provider', 'azure', '--resource-group', 'kubelab-testing'], capture_output=True, text=True)
        print("Use command for azure cluster result:", result.stdout)
        assert result.returncode == 0
        print("Use for Azure cluster has pass all the test")