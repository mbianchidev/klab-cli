import subprocess
import pytest
import os

class TestGCPNginx:
    def test_init(self):
        print("Running test_init")
        os.chdir(os.path.join(os.path.dirname(__file__), '..'))
        print("Changed directory to:", os.getcwd())
        result = subprocess.run(['python3', 'lab.py', 'init'], capture_output=True, text=True)
        print("Init result:", result.stdout)
        assert result.returncode == 0

    def test_create_gcp_cluster(self):
        print("Running test create cluster in GCP")
        os.chdir(os.path.join(os.path.dirname(__file__), '..'))
        result = subprocess.run(['python3', 'lab.py', 'create', 'cluster', '-pr', 'GCP', '-cn', 'gke', '-p', 'cts-project-388707', '-r', 'europe-central2'], capture_output=True, text=True)
        print("GCP create cluster result:", result.stdout)
        assert result.returncode == 0

if __name__ == '__main__':
    pytest.main()