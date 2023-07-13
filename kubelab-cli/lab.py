#!/usr/bin/env python3

import click
import os
import subprocess
import json
from catalog.nginx.deploy import Deploy
import shutil


@click.group()
def cli():
    pass


@cli.command()
def init():
    script_dir = os.path.dirname(os.path.realpath(__file__))
    credentials_dir = os.path.join(script_dir, 'credentials')
    os.makedirs(credentials_dir, exist_ok=True)

    # Check if AWS CLI is installed and configured
    try:
        subprocess.run(['aws', '--version'], check=True, capture_output=True, text=True)
        aws_credentials_file = os.path.join(credentials_dir, 'aws_kube_credential')

        if os.path.isfile(aws_credentials_file):
            os.remove(aws_credentials_file)

        shutil.copy(os.path.expanduser('~/.aws/credentials'), aws_credentials_file)

        click.echo(f'Credentials saved to {aws_credentials_file}')
        print("Initializing Terraform...")
        os.chdir('../AWS')
        subprocess.run(['terraform', 'init'])
    except subprocess.CalledProcessError:
        click.echo('AWS CLI is not installed. Please install and configure it before proceeding.')

    # Check if Azure CLI is installed and configured
    try:
        subprocess.run(['az', '--version'], check=True, capture_output=True, text=True)
        result = subprocess.run(['az', 'account', 'show'], capture_output=True, text=True)
        if result.returncode == 0:
            output = result.stdout.strip()
            azure_credentials_file = os.path.join(credentials_dir, 'azure_kube_credential.json')

            with open(azure_credentials_file, 'w') as f:
                f.write(output)

            click.echo(f'Credentials saved to {azure_credentials_file}')
            print("Initializing Terraform...")
            os.chdir('../Azure')
            subprocess.run(['terraform', 'init'])
        else:
            click.echo('Azure login failed. Please make sure Azure CLI is installed and logged in.')
    except subprocess.CalledProcessError:
        click.echo('Azure CLI is not installed. Please install and configure it before proceeding.')

    # Check if gcloud CLI is installed and configured
    try:
        subprocess.run(['gcloud', '--version'], check=True, capture_output=True, text=True)
        gcp_credentials_file = os.path.join(credentials_dir, 'gcp_kube_credential.json')

        if os.path.isfile(gcp_credentials_file):
            os.remove(gcp_credentials_file)

        shutil.copy(os.path.expanduser('~/.config/gcloud/application_default_credentials.json'), gcp_credentials_file)

        click.echo(f'Credentials saved to {gcp_credentials_file}')
        print("Initializing Terraform...")
        os.chdir('../GCP')
        subprocess.run(['terraform', 'init'])
    except subprocess.CalledProcessError:
        click.echo('gcloud CLI is not installed. Please install and configure it before proceeding.')

@cli.command()
@click.argument('name', type=click.Choice(['cluster', 'role', 'rbac']))
@click.option('-cp', '--cloud-provider', type=click.Choice(['AWS', 'Azure', 'GCP']), help='Cloud provider', required=True)
def create(name, cloud_provider):
    if name == 'role':
        click.echo("This feature will be available soon")
    elif name == 'cluster' and cloud_provider == "AWS":
        region = 'eu-west-1'  # Default region for AWS
        region_file_path = 'credentials/aws_kube_config'
        with open(region_file_path, 'w') as f:
            f.write(f"{region}")

        print(f"Creating cluster in {cloud_provider} and {region} region")
        os.chdir('../AWS')
        subprocess.run(['terraform', 'apply', '-auto-approve'])
    elif name == 'cluster' and cloud_provider == "Azure":
        print(f"Creating cluster in {cloud_provider}")
        os.chdir('../Azure')
        subprocess.run(['terraform', 'apply', '-auto-approve'])
    elif name == 'cluster' and cloud_provider == "GCP":
        print(f"Creating cluster in {cloud_provider}")
        os.chdir('../GCP')
        subprocess.run(['terraform', 'apply', '-auto-approve'])
    elif name == 'rbac':
        click.echo("This feature will be available soon")


# There is a bug for the destroy function
# This function currently destroys everything for the Cloud provider, not only the cluster.
# You can basicly run bash lab destroy cluster a b // It will destroy everything for the provider that you are initialized.
@cli.command()
@click.argument('param_type', type=click.Choice(['cluster', 'role', 'rbac']))
@click.argument('name', type=click.STRING, required=True)
@click.argument('region', type=click.STRING, required=True)
def destroy(param_type, name, region):
    region_file_path = 'credentials/aws_kube_config'
    with open(region_file_path, 'w') as f:
        f.write(f"{region}")

    with open('state/lab_state.json', 'r') as file:
        data = json.load(file)
        initialized_cloud_provider = data.get('initialized_cloud_provider')
    if param_type == 'role':
        click.echo("This feature will be available soon")
    elif param_type == 'cluster' and initialized_cloud_provider == "AWS":
        print(f"Deleting cluster with name {name} provider {initialized_cloud_provider} and {region} region")
        os.chdir('../AWS')
        subprocess.run(['terraform', 'destroy', '-auto-approve'])
    elif param_type == 'cluster' and initialized_cloud_provider == "Azure":
        print(f"Deleting cluster with name {name} provider {initialized_cloud_provider} and {region} region")
        os.chdir('../Azure')
        subprocess.run(['terraform', 'destroy', '-auto-approve'])
    elif param_type == 'cluster' and initialized_cloud_provider == "GCP":
        print(f"Deleting cluster with name {name} provider {initialized_cloud_provider} and {region} region")
        os.chdir('../GCP')
        subprocess.run(['terraform', 'destroy', '-auto-approve'])
    elif param_type == 'rbac':
        click.echo("This feature will be available soon")


@cli.command()
def test():
    deployer = Deploy(type)
    deployer.operator('operator')
    deployer.deployment('deployment')


@cli.command()
@click.option('--type', type=click.Choice(['operator', 'deployment']), required=False, default="deployment", help='Type of how to deploy operator')
@click.argument('product', type=click.Choice(['nginx', 'istio', 'karpenter']))
@click.option('--version', type=click.STRING, default='1.5.0', help="Operator version", required=False)
def add(type, product, version):
    product_cat = dict()
    installed_type = dict()
    with open("catalog/catalog.yaml", 'r') as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            if line.startswith('- product'):
                product_cat['product'] = line.split(':')[1].strip()
            elif line.startswith('installed_type'):
                installed_type['installed_type'] = line.split(':')[1].strip()
    if installed_type['installed_type'] == "deployment":
        answer = input("NGINX is already installed, do you want to switch from the current installation (deployment - latest) to an operator based one? (Y/N): ")
        if answer == 'y':
            print("Deleting the deployment and switching to operator \n")
            type = 'operator'
            deploy_repo = "catalog/nginx/nginx_deployment"
            os.chdir(deploy_repo)
            process = subprocess.Popen(['kubectl', 'delete', '-f', 'deployment.yaml'], stdout=subprocess.PIPE, universal_newlines=True )
            exit_code = process.wait()
            if exit_code == 0:
                print("Succesfull deleted nginx deployment \n")
            else:
                print("Deployment failed")
            os.chdir('../../..')
        elif answer == 'n':
            print("Staying in deployment")
            exit()
    if installed_type['installed_type'] == "operator":
        answer = input(f"NGINX is already installed, do you want to switch from the current installation (operator - {version}) to an deployment based one? (Y/N): ")
        if answer == 'y':
            print("Deleting operator and switching to deployment \n")
            type = 'deployment'
            repo_dir = 'catalog/nginx/nginx-ingress-helm-operator'
            os.chdir(repo_dir)
            # Delete the deployed operator
            process = subprocess.Popen(['make', 'undeploy'], stdout=subprocess.PIPE, universal_newlines=True)
            exit_code = process.wait()
            if exit_code == 0:
                print(f"Succesfully deleted nginx operator {version} version\n")
            else:
                print("Deployment failed")
            os.chdir('../../../')
        elif answer == 'n':
            print("Keeping the deployment installed.")
            exit()
    elif type == 'operator' and product == 'nginx':
        deploy = Deploy(op_version=version)
        deploy.operator()
    if type == 'deployment' and product == 'nginx':
        deploy = Deploy()
        deploy.deployment()


@cli.command()
@click.option('--type', type=click.Choice(['operator', 'deployment']), help='Type of how to deploy operator')
@click.argument('product', type=click.Choice(['nginx', 'istio', 'karpenter']))
@click.option('--version', type=click.STRING, default='1.4.1', help="Operator version", required=False)
def update(type, product, version):
    if type == 'operator' and product == 'nginx':
        print(f'Upadating NGINX with latest version ({version})')
        repo_dir = 'catalog/nginx/nginx-ingress-helm-operator'
        if not os.path.exists(repo_dir):
            subprocess.run(['git', 'clone', 'https://github.com/nginxinc/nginx-ingress-helm-operator/',
                            '--branch', f'v{version}'])
        os.chdir(repo_dir)
        subprocess.run(['git', 'checkout', f'v{version}'])
        # Update the Operator
        img = f'nginx/nginx-ingress-operator:{version}'
        subprocess.run(['make', 'deploy', f'IMG={img}'])
        subprocess.run(['kubectl', 'get', 'deployments', '-n', 'nginx-ingress-operator-system'])

        print(f'Nginx operator updated successfully with {version} version')
    elif type == 'deployment' and product == 'nginx':
        print("Cant't update via deployment type must be changed in the yaml manifest.")
    else:
        print('Invalid configuration.')


@cli.command()
@click.option('--type', type=click.Choice(['operator', 'deployment']), help='Type of how to deploy operator')
@click.argument('product', type=click.Choice(['nginx', 'istio', 'karpenter']))
@click.option('--version', type=click.STRING, default='1.4.1', help="Operator version", required=False)
def delete(type, product, version):
    if type == 'operator' and product == 'nginx':
        print(f'Deleting NGINX with {version} version')
        repo_dir = 'catalog/nginx/nginx-ingress-helm-operator'
        os.chdir(repo_dir)
        # Delete the deployed operator
        subprocess.run(['make', 'undeploy'])
        data = [
            {
                'product': 'nginx',
                'default_version': 'latest',
                'default_type': 'deployment',
                'available_types': ['deployment', 'operator'],
                'installed_version': 'latest',
                'installed_type': ''
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
        print(f'Nginx operator deleted successfully with {version} version')
    elif type == 'deployment' and product == 'nginx':
        print("Deleting nginx deployment with latest image version")
        deploy_repo = "catalog/nginx/nginx_deployment"
        os.chdir(deploy_repo)
        subprocess.run(['kubectl', 'delete', '-f', 'deployment.yaml'])
        data = [
            {
                'product': 'nginx',
                'default_version': 'latest',
                'default_type': 'deployment',
                'available_types': ['deployment', 'operator'],
                'installed_version': 'latest',
                'installed_type': ''
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
    else:
        print('Invalid configuration.')


@cli.command()
@click.argument('cluster', type=click.STRING)
@click.option('--region', type=click.STRING, help='Region of the cluster')
@click.option('--resource-group', type=click.STRING, help='Resource group of the cluster')
def use(cluster, region, resource_group):
    with open('state/lab_state.json', 'r') as file:
        data = json.load(file)
        initialized_cloud_provider = data.get('initialized_cloud_provider')

    if initialized_cloud_provider == "AWS":
        if region is None:
            print("Region is required for AWS, use --region <YOUR-CLUSTER-REGION> while running the command.")
            return
        subprocess.run(["aws", "eks", "update-kubeconfig", "--region", region, "--name", cluster])
    elif initialized_cloud_provider == "Azure":
        if resource_group is None:
            print("Resource group is required for Azure, use --resource-group <YOUR-RESOURCE-GROUP> while running the command.")
            return
        subprocess.run(["az", "aks", "get-credentials", "--resource-group", resource_group, "--name", cluster, "--overwrite-existing"])
    elif initialized_cloud_provider == "GCP":
        if region is None:
            print("Region is required for GCP, use --region <YOUR-CLUSTER-REGION> while running the command.")
            return
        subprocess.run(["gcloud", "container", "clusters", "get-credentials", cluster, "--region=" + region])
    else:
        print("Unsupported cloud provider.")
        return


@cli.command()
def info():
    print("Information about your cluster come from cnquery lib - thanks mondoo")
    subprocess.run(['cnquery', 'shell', 'k8s'])


if __name__ == '__main__':
    cli()
