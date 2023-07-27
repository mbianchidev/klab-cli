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
        result = subprocess.run(['python3', 'lab.py', 'create', 'cluster', '-cn', 'eks', '-pr' 'AWS', '-r', 'eu-west-2'], capture_output=True, text=True)
        print("AWS create cluster result:", result.stdout)
        assert result.returncode == 0
        print("AWS cluster has been created!")


if __name__ == '__main__':
    pytest.main()
