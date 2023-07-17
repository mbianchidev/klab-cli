import os
import subprocess


class Deploy:
    def __init__(self, op_version=None):
        # Constructor code here
        self.op_version = op_version
        pass

    def deployment(self):
        # Deployment code here
        deploy_repo = "catalog/nginx/nginx_deployment"
        os.chdir(deploy_repo)
        process = subprocess.Popen(['kubectl', 'apply', '-f', 'deployment.yaml'], stdout=subprocess.PIPE, universal_newlines=True)
        print("Installing nginx with deployment and latest image version \n ")
        exit_code = process.wait()
        if exit_code == 0:
            print("Successfully deployed nginx with deployment \n ")
        else:
            print("Deployment failed")
        data = [
            {
                'product': 'nginx',
                'default_version': 'latest',
                'default_type': 'deployment',
                'available_types': ['deployment', 'operator'],
                'installed_version': 'latest',
                'installed_type': 'deployment'
            },
        ]
        with open('../../catalog.yaml', 'w') as file:
            for item in data:
                file.write("- product: {}\n".format(item['product']))
                file.write("  default_version: {}\n".format(item['default_version']))
                file.write("  default_type: {}\n".format(item['default_type']))
                file.write("  available_types:\n")
                for available_type in item['available_types']:
                    file.write("    - {}\n".format(available_type))
                file.write("  installed_version: {}\n".format(item['installed_version']))
                file.write("  installed_type: {}\n\n".format(item['installed_type']))

    def operator(self):
        # Operator code here
        repo_dir = 'catalog/nginx/nginx-ingress-helm-operator'
        if not os.path.exists(repo_dir):
            subprocess.run(['git', 'clone', 'https://github.com/nginxinc/nginx-ingress-helm-operator/',
                            '--branch', f'v{self.op_version}'])
        os.chdir(repo_dir)
        print(f'Adding NGINX operator with {self.op_version} version\n')
        subprocess.run(['git', 'checkout', f'v{self.op_version}'])
        # Deploy the Operator
        img = f'nginx/nginx-ingress-operator:{self.op_version}'
        process = subprocess.Popen(['make', 'deploy', f'IMG={img}'], stdout=subprocess.PIPE, universal_newlines=True)
        exit_code = process.wait()
        if exit_code == 0:
            print(f"Succesfully deployed nginx with operator {self.op_version} version\n")
        else:
            print("Deployment failed")
        data = [
            {
                'product': 'nginx',
                'default_version': self.op_version,
                'default_type': 'deployment',
                'available_types': ['deployment', 'operator'],
                'installed_version': self.op_version,
                'installed_type': 'operator'
            },
        ]
        with open('../../catalog.yaml', 'w') as file:
            for item in data:
                file.write("- product: {}\n".format(item['product']))
                file.write("  default_version: {}\n".format(item['default_version']))
                file.write("  default_type: {}\n".format(item['default_type']))
                file.write("  available_types:\n")
                for available_type in item['available_types']:
                    file.write("    - {}\n".format(available_type))
                file.write("  installed_version: {}\n".format(item['installed_version']))
                file.write("  installed_type: {}\n\n".format(item['installed_type']))
<<<<<<< HEAD
        pass
=======
        pass
>>>>>>> 4c7de70 (Update lab CLI, GCP and tests)
