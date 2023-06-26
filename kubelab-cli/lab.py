#!/usr/bin/env python3

import click
import boto3
import os
import subprocess


@click.group()
def cli():
    pass


@cli.command()
@click.option('-cp', type=click.Choice(['AWS', 'Azure', 'GCP']), help='Type of cloud provider')
@click.pass_context
def init(ctx, cp):
    ctx.obj = {
        'cloud_provider': cp
    }
    if cp == 'AWS':
        # Check if the AWS credentials file exists
        aws_credentials_file = os.path.expanduser('~/.aws/credentials')
        if os.path.isfile(aws_credentials_file):
            # Read the AWS credentials from the file
            aws_credentials = dict()
            with open(aws_credentials_file, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    line = line.strip()
                    if line.startswith('aws_access_key_id'):
                        aws_credentials['aws_access_key_id'] = line.split('=')[1].strip()
                    elif line.startswith('aws_secret_access_key'):
                        aws_credentials['aws_secret_access_key'] = line.split('=')[1].strip()

            # Save the credentials to a file
            credential_file_path = 'credentials/aws_kube_credential.txt'
            with open(credential_file_path, 'w') as f:
                f.write(f"AWS Access Key ID: {aws_credentials['aws_access_key_id']}\n")
                f.write(f"AWS Secret Access Key: {aws_credentials['aws_secret_access_key']}\n")
                click.echo(f'Credentials saved to {credential_file_path}')
        else:
            click.echo('AWS credentials file not found. Please enter the credentials.')
            aws_access_key_id = click.prompt('AWS Access Key ID')
            aws_secret_access_key = click.prompt('AWS Secret Access Key', hide_input=True)

            # Save the credentials to a file
            credential_file_path = 'credential/aws_kube_credential.txt'
            with open(credential_file_path, 'w') as f:
                f.write(f"AWS Access Key ID: {aws_access_key_id}\n")
                f.write(f"AWS Secret Access Key: {aws_secret_access_key}\n")
                click.echo(f'Credentials saved to {credential_file_path}')

            session = boto3.Session(
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key
            )
    elif cp == "Azure":
        print("taking crednential from Azure ")    
    else:
        click.echo('Unsupported credentials provider.')


@cli.command()
@click.argument('param_type', type=click.Choice(['cluster', 'role', 'rbac']))
@click.pass_context
def create(ctx, param_type):
    cloud_provider = ctx.obj.get('cloud_provider')
    if param_type == 'role':
        click.echo("This feature will be available soon")
    elif param_type == 'cluster' and cloud_provider == "AWS":
        print(f"Creatin cluster in {cloud_provider}")
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


if __name__ == '__main__':
    cli()
