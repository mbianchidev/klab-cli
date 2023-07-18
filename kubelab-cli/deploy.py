import os
import subprocess


class Deploy:
    def __init__(self, deployment_type=None, operatorRepo=None, op_version=None):
        # Constructor code here
        self.op_version = op_version
        self.deployment_type = deployment_type
        self.operatorRepo = operatorRepo
        pass

    def deployment(self):
        # Deployment code here
        process = subprocess.Popen(['kubectl', 'apply', '-f', self.deployment_type], stdout=subprocess.PIPE, universal_newlines=True)
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
                'installed_type': 'deployment',
                'operatorRepo':' https://github.com/nginxinc/nginx-ingress-helm-operator/',
                'operatorVersion': self.op_version,
                'deploymentFile': self.deployment_type
            },
        ]
        with open('catalog/catalog.yaml', 'w') as file:
            for item in data:
                file.write("- product: {}\n".format(item['product']))
                file.write("  default_version: {}\n".format(item['default_version']))
                file.write("  default_type: {}\n".format(item['default_type']))
                file.write("  available_types:\n")
                for available_type in item['available_types']:
                    file.write("    - {}\n".format(available_type))
                file.write("  installed_version: {}\n".format(item['installed_version']))
                file.write("  installed_type: {}\n".format(item['installed_type']))
                file.write("  operatorRepo: {}\n".format(item['operatorRepo']))
                file.write("  operatorVersion: {}\n".format(item['operatorVersion']))
                file.write("  deploymentFile: {}\n\n".format(item['deploymentFile']))

    def operator(self):
        # Operator code here
        repo_dir = 'catalog/nginx/nginx-ingress-helm-operator'
        if not os.path.exists(repo_dir):
            subprocess.run(['git', 'clone', self.operatorRepo,
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
                'installed_type': 'operator',
                'operatorRepo':' https://github.com/nginxinc/nginx-ingress-helm-operator/',
                'operatorVersion': self.op_version,
                'deploymentFile': 'catalog/nginx/nginx_deployment/deployment.yaml'
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
                file.write("  installed_type: {}\n".format(item['installed_type']))
                file.write("  operatorRepo: {}\n".format(item['operatorRepo']))
                file.write("  operatorVersion: {}\n".format(item['operatorVersion']))
                file.write("  deploymentFile: {}\n\n".format(item['deploymentFile']))           
        pass

    def switch_operator(self):
        answer = input("NGINX is already installed, do you want to switch from the current installation (deployment - latest) to an operator based one? (Y/N): ")
        if answer == 'y':
            print("Deleting the deployment and switching to operator \n")
            deploy_repo = "catalog/nginx/nginx_deployment"
            os.chdir(deploy_repo)
            process = subprocess.Popen(['kubectl', 'delete', '-f', 'deployment.yaml'], stdout=subprocess.PIPE, universal_newlines=True )
            exit_code = process.wait()
            if exit_code == 0:
                print("Successfully deleted nginx deployment \n")
            else:
                print("Deployment failed")
            os.chdir('../../..')
        elif answer == 'n':
            print("Staying in deployment")
            exit()

    def switch_deployment(self):
        answer = input(f"NGINX is already installed, do you want to switch from the current installation (operator - {self.op_version}) to an deployment based one? (Y/N): ")
        if answer == 'y':
            print("Deleting operator and switching to deployment \n")     
            repo_dir = 'catalog/nginx/nginx-ingress-helm-operator'
            os.chdir(repo_dir)
            # Delete the deployed operator
            process = subprocess.Popen(['make', 'undeploy'], stdout=subprocess.PIPE, universal_newlines=True)
            exit_code = process.wait()
            if exit_code == 0:
                print(f"Successfully deleted nginx operator {self.op_version} version\n")
            else:
                print("Deployment failed")
            os.chdir('../../../')
        elif answer == 'n':
            print("Keeping the deployment installed.")
            exit()
