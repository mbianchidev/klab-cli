import os
import subprocess
import yaml
import re


class Deploy:
    def __init__(self, productName, installed_type=None, imageVersion=None, deployment_type=None, operatorImage=None, operatorRepo=None, op_version=None, operatorDir=None):
        # Constructor code here
        self.op_version = op_version
        self.deployment_type = deployment_type
        self.operatorRepo = operatorRepo
        self.productName = productName
        self.installed_type = installed_type
        self.operatorDir = operatorDir
        self.operatorImage = operatorImage
        self.imageVersion = imageVersion
        pass

    def deployment(self, productName, operatorRepo):
        # Deployment code here
        with open(self.deployment_type, "r") as f:
            yaml_content = f.read()

        new_image_version = self.imageVersion
        pattern = r"(image:\s*[\w/-]+:)(.*)"
        yaml_content = re.sub(pattern, f"image: {productName}:{new_image_version}", yaml_content)

        with open(self.deployment_type, "w") as f:
            f.write(yaml_content)

        process = subprocess.Popen(['kubectl', 'apply', '-f', self.deployment_type], stdout=subprocess.PIPE, universal_newlines=True)
        print(f"Installing {productName} with deployment and {self.imageVersion} image version \n ")
        exit_code = process.wait()
        if exit_code == 0:
            print(f"Successfully deployed {productName} with deployment \n ")
        else:
            print("Deployment failed")
        data = [
            {
                'product': productName,
                'default_version': 'latest',
                'default_type': 'deployment',
                'available_types': ['deployment', 'operator'],
                'installed_version': self.imageVersion,
                'installed_type': self.installed_type,
                'operatorRepo': operatorRepo,
                'operatorVersion': self.op_version,
                'operatorImage': self.operatorImage,
                'operatorDir': self.operatorDir,
                'deploymentFile': self.deployment_type,
                'imageVersion': self.imageVersion
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
                file.write("  operatorImage: {}\n".format(item['operatorImage']))
                file.write("  operatorDir: {}\n".format(item['operatorDir']))
                file.write("  deploymentFile: {}\n".format(item['deploymentFile']))
                file.write("  imageVersion: {}\n\n".format(item['imageVersion']))

    def operator(self,  productName, operatorRepo):
        # Operator code here
        repo_dir = self.operatorDir
        if not os.path.exists(repo_dir):
            subprocess.run(['git', 'clone', operatorRepo,
                            '--branch', f'v{self.op_version}'])
        os.chdir(repo_dir)
        print(f'Adding {productName} operator with {self.op_version} version\n')
        subprocess.run(['git', 'checkout', f'v{self.op_version}'])
        # Deploy the Operator
        img = f'{self.operatorImage}:{self.op_version}'
        process = subprocess.Popen(['make', 'deploy', f'IMG={img}'], stdout=subprocess.PIPE, universal_newlines=True)
        exit_code = process.wait()
        if exit_code == 0:
            print(f"Succesfully deployed {productName} with operator {self.op_version} version\n")
        else:
            print("Deployment failed")
        data = [
            {
                'product': productName,
                'default_version': self.op_version,
                'default_type': 'deployment',
                'available_types': ['deployment', 'operator'],
                'installed_version': self.op_version,
                'installed_type': self.installed_type,
                'operatorRepo': operatorRepo,
                'operatorVersion': self.op_version,
                'operatorImage': self.operatorImage,
                'operatorDir': self.operatorDir,
                'deploymentFile': self.deployment_type,
                'imageVersion': self.imageVersion
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
                file.write("  operatorImage: {}\n".format(item['operatorImage']))
                file.write("  operatorDir: {}\n".format(item['operatorDir']))
                file.write("  deploymentFile: {}\n".format(item['deploymentFile']))
                file.write("  imageVersion: {}\n\n".format(item['imageVersion']))
        pass

    def switch_operator(self, productName):
        answer = input(f"{productName} is already installed, do you want to switch from the current installation (deployment - latest) to an operator based one? (Y/N): ")
        if answer == 'y':
            print("Deleting the deployment and switching to operator \n")
            deploy_repo = "catalog/nginx/nginx_deployment"
            os.chdir(deploy_repo)
            process = subprocess.Popen(['kubectl', 'delete', '-f', 'deployment.yaml'], stdout=subprocess.PIPE, universal_newlines=True )
            exit_code = process.wait()
            if exit_code == 0:
                print(f"Successfully deleted {productName} deployment \n")
            else:
                print("Deployment failed")
            os.chdir('../../..')
        elif answer == 'n':
            print("Staying in deployment")
            exit()

    def switch_deployment(self, productName):
        answer = input(f"{productName} is already installed, do you want to switch from the current installation (operator - {self.op_version}) to an deployment based one? (Y/N): ")
        if answer == 'y':
            print("Deleting operator and switching to deployment \n")     
            repo_dir = self.operatorDir
            os.chdir(repo_dir)
            # Delete the deployed operator
            process = subprocess.Popen(['make', 'undeploy'], stdout=subprocess.PIPE, universal_newlines=True)
            exit_code = process.wait()
            if exit_code == 0:
                print(f"Successfully deleted {productName} operator {self.op_version} version\n")
            else:
                print("Deployment failed")
            os.chdir('../../../')
        elif answer == 'n':
            print("Keeping the deployment installed.")
            exit()
