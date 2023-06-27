#!/usr/bin/env python3

import click
import boto3
import os
import subprocess
import json


@click.group()
def cli():
    pass


@cli.command()
@click.option('-cp', type=click.Choice(['AWS', 'Azure', 'GCP']), help='Type of cloud provider')
def init(cp):
    if cp == 'AWS':
        # Check if the AWS credentials file exists
        aws_credentials_file = os.path.expanduser('~/.aws/credentials')
        if os.path.isfile(aws_credentials_file):
            # Set the destination file path
            credential_file_path = 'credentials/aws_kube_credential'

            # Copy the AWS credentials file
            with open(aws_credentials_file, 'r') as src_file, open(credential_file_path, 'w') as dest_file:
                dest_file.write(src_file.read())

            click.echo(f'Credentials saved to {credential_file_path}')

            # Save the state
            state = {'initialized_cloud_provider': 'AWS'}
            state_file_path = 'state/lab_state.json'
            os.makedirs(os.path.dirname(state_file_path), exist_ok=True)  # Create 'state' folder if it doesn't exist
            with open(state_file_path, 'w') as f:
                json.dump(state, f)
            click.echo(f'State saved to {state_file_path}')
        else:
            click.echo('AWS credentials file not found. Please enter the credentials.')
            profile = click.prompt('AWS Profile')
            aws_access_key_id = click.prompt('AWS Access Key ID')
            aws_secret_access_key = click.prompt('AWS Secret Access Key', hide_input=True)

            # Save the credentials to a file
            credential_file_path = 'credentials/aws_kube_credential'
            with open(credential_file_path, 'w') as f:
                f.write(f"[{profile}]\n")
                f.write(f"aws_access_key_id = {aws_access_key_id}\n")
                f.write(f"aws_secret_access_key = {aws_secret_access_key}\n")
            click.echo(f'Credentials saved to {credential_file_path}')

            # Save the state
            state = {'initialized_cloud_provider': 'AWS'}
            state_file_path = 'state/lab_state.json'
            os.makedirs(os.path.dirname(state_file_path), exist_ok=True)  # Create 'state' folder if it doesn't exist
            with open(state_file_path, 'w') as f:
                json.dump(state, f)
            click.echo(f'State saved to {state_file_path}')

    elif cp == 'Azure':
        try:
            # Use Azure CLI to retrieve the currently logged-in Azure account
            result = subprocess.run(['az', 'account', 'show'], capture_output=True, text=True)
            if result.returncode == 0:
                output = result.stdout.strip()

                # Save the credentials to a file
                credential_file_path = 'credentials/azure_kube_credential.json'
                with open(credential_file_path, 'w') as f:
                    f.write(output)
                click.echo(f'Credentials saved to {credential_file_path}')

                # Save the state
                state = {'initialized_cloud_provider': 'Azure'}
                state_file_path = 'state/lab_state.json'
                os.makedirs(os.path.dirname(state_file_path), exist_ok=True)  # Create 'state' folder if it doesn't exist
                with open(state_file_path, 'w') as f:
                    json.dump(state, f)
                click.echo(f'State saved to {state_file_path}')
            else:
                click.echo('Azure login failed. Please make sure Azure CLI is installed and logged in.')
        except Exception as e:
            click.echo(f'Error occurred while retrieving Azure credentials: {str(e)}')
    else:
        click.echo('Unsupported credentials provider.')


@cli.command()
@click.argument('name', type=click.Choice(['cluster', 'role', 'rbac']))
@click.option('--region', type=click.STRING, default='eu-west-1', help="Region in which EKS will be deployed", required=False)
def create(name, region):
    region_file_path = 'credentials/aws_kube_config'
    with open(region_file_path, 'w') as f:
        f.write(f"{region}")

    with open('state/lab_state.json', 'r') as file:
        data = json.load(file)
        initialized_cloud_provider = data.get('initialized_cloud_provider')
    if name == 'role':
        click.echo("This feature will be available soon")
    elif name == 'cluster' and initialized_cloud_provider == "AWS":
        print(f"Creating cluster in {initialized_cloud_provider} and {region} region")
        os.chdir('../AWS')
        subprocess.run(['terraform', 'apply', '-auto-approve'])
    elif name == 'cluster' and initialized_cloud_provider == "Azure":
        print(f"Creating cluster in {initialized_cloud_provider} ")
        os.chdir('../Azure')
        subprocess.run(['terraform', 'apply', '-auto-approve'])
    elif name == 'rbac':
        click.echo("This feature will be available soon")


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
        os.chdir('../AWS')
        subprocess.run(['terraform', 'destroy', '-auto-approve'])
    elif param_type == 'rbac':
        click.echo("This feature will be available soon")


@cli.command()
@click.option('--type', type=click.Choice(['operator', 'deployment']), help='Type of how to deploy operator')
@click.argument('product', type=click.Choice(['nginx', 'istio', 'karpenter']))
@click.option('--version', type=click.STRING, default='1.4.2', help="Operator version", required=False)
def add(type, product, version):
    if type == 'operator' and product == 'nginx':
        print(f'Adding NGINX with {version} version')
        repo_dir = 'nginx-ingress-helm-operator'
        if not os.path.exists(repo_dir):
            subprocess.run(['git', 'clone', 'https://github.com/nginxinc/nginx-ingress-helm-operator/',
                            '--branch', f'v{version}'])
        os.chdir(repo_dir)
        # Deploy the Operator
        img = f'nginx/nginx-ingress-operator:{version}'
        subprocess.run(['make', 'deploy', f'IMG={img}'])
        subprocess.run(['kubectl', 'get', 'deployments', '-n', 'nginx-ingress-operator-system'])

        print(f'Nginx operator installed successfully with {version} version')
    elif type == 'deployment' and product == 'nginx':
        print("Installing nginx with deployment and lattest version")
        deploy_repo = "nginx_deployment"
        os.chdir(deploy_repo)
        subprocess.run(['kubectl', 'apply', '-f', 'deployment.yaml'])
    else:
        print('Invalid configuration.')


@cli.command()
@click.option('--type', type=click.Choice(['operator', 'deployment']), help='Type of how to deploy operator')
@click.argument('product', type=click.Choice(['nginx', 'istio', 'karpenter']))
@click.option('--version', type=click.STRING, default='1.4.2', help="Operator version", required=False)
def update(type, product, version):
    if type == 'operator' and product == 'nginx':
        print(f'Upadating NGINX with latest {version} version')
        repo_dir = 'nginx-ingress-helm-operator'
        if not os.path.exists(repo_dir):
            subprocess.run(['git', 'clone', 'https://github.com/nginxinc/nginx-ingress-helm-operator/',
                            '--branch', f'v{version}'])
        os.chdir(repo_dir)
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
@click.option('--version', type=click.STRING, default='1.4.2', help="Operator version", required=False)
def delete(type, product, version):
    if type == 'operator' and product == 'nginx':
        print(f'Deleting NGINX with {version} version')
        repo_dir = 'nginx-ingress-helm-operator'
        os.chdir(repo_dir)
        # Delete the deployed operator
        subprocess.run(['make', 'undeploy'])

        print(f'Nginx operator deleted successfully with {version} version')
    elif type == 'deployment' and product == 'nginx':
        print("Deleting nginx deployment with lattest version")
        deploy_repo = "nginx_deployment"
        os.chdir(deploy_repo)
        subprocess.run(['kubectl', 'delete', '-f', 'deployment.yaml'])
    else:
        print('Invalid configuration.')


@cli.command()
def info():
    return "Hello"


@cli.command()
@click.argument('name', type=click.Choice(['cluster', 'role', 'rbac']))
@click.argument('cluster', type=click.STRING, required=True)
@click.argument('region', type=click.STRING,  required=True)
def use(name, cluster, region):
    with open('state/lab_state.json', 'r') as file:
        data = json.load(file)
        initialized_cloud_provider = data.get('initialized_cloud_provider')
    if initialized_cloud_provider == "AWS":
        subprocess.run(["aws", "eks", "update-kubeconfig", "--region", region, "--name", cluster])
    elif initialized_cloud_provider == "Azure":
        print("Will be updated soon")


if __name__ == '__main__':
    cli()
