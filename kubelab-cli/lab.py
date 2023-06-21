#!/usr/bin/env python3

import click
import boto3
import os
import argparse
import logging
import subprocess
import yaml
from jinja2 import Environment, FileSystemLoader


@click.group()
def cli():
    pass


@cli.command()
@click.option('-cp', '--credentials-provider', type=str, help='Credentials provider')
def init(credentials_provider):
    if credentials_provider == 'AWS':
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
            credential_file_path = 'credentials/kube_credential.txt'
            with open(credential_file_path, 'w') as f:
                f.write(f"AWS Access Key ID: {aws_credentials['aws_access_key_id']}\n")
                f.write(f"AWS Secret Access Key: {aws_credentials['aws_secret_access_key']}\n")
                click.echo(f'Credentials saved to {credential_file_path}')
        else:
            click.echo('AWS credentials file not found. Please enter the credentials.')
            aws_access_key_id = click.prompt('AWS Access Key ID')
            aws_secret_access_key = click.prompt('AWS Secret Access Key', hide_input=True)

            # Save the credentials to a file
            credential_file_path = 'credential/kube_credential.txt'
            with open(credential_file_path, 'w') as f:
                f.write(f"AWS Access Key ID: {aws_access_key_id}\n")
                f.write(f"AWS Secret Access Key: {aws_secret_access_key}\n")
                click.echo(f'Credentials saved to {credential_file_path}')

            session = boto3.Session(
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key
            )
    else:
        click.echo('Unsupported credentials provider.')


# def open_file(ctx, param, value):
#     if value:
#         return open(value, 'r')
#     else:
#         return None


class TemplateGenerator:
    CUR_DIR_PATH = os.path.dirname(os.path.abspath(__file__))
    TESTING_DIR = os.path.abspath(os.path.join(CUR_DIR_PATH, 'Testing'))


@cli.command()
@click.option('--file', type=click.Path(exists=True), help='Path to the config file in yaml format',)
@click.argument('param_type', type=click.Choice(['cluster', 'role', 'rbac']))
@click.argument('cloud_provider', type=click.Choice(['AWS', 'AZURE', 'GCP']))
@click.argument('module', type=click.Choice(['EKS', 'EBS', 'S3']))
def create(param_type, cloud_provider, module, file):
    if file is None:
        click.echo('Config file not provided.')
    else:
        if param_type == 'role':
            click.echo("This feature will be available soon")
        elif param_type == 'cluster':
            try:
                dir_path_tf = os.path.abspath(os.path.join(TemplateGenerator.CUR_DIR_PATH, cloud_provider, module))
                conf_path = os.path.join(dir_path_tf, f'{file}')

                with open(conf_path) as file:
                    conf_var = yaml.safe_load(file)

                file_loader = FileSystemLoader(dir_path_tf)

                env = Environment(loader=file_loader, autoescape=True)

                jinja_template = env.get_template(conf_var['template_path'])
                output = jinja_template.render(conf_var)

                os.makedirs(TemplateGenerator.TESTING_DIR, exist_ok=True)
                output_path = os.path.join(TemplateGenerator.TESTING_DIR, 'output-tf.tf')
                with open(output_path, 'w') as f:
                    f.write(output)
                print("Your template is created")
                ter_dir = os.path.join(TemplateGenerator.TESTING_DIR)
                os.chdir(ter_dir)
                subprocess.run(['terraform', 'init'])
                subprocess.run(['terraform', 'plan'])
                return output
            except Exception as err:
                logging.exception("Can't generate Terraform template")
                return str(err)
            # if file.name == 'eks_cluster.yaml':
            #     print("Creating cluster with conf from this file: ", file.name)
            #     subprocess.run(['python3', 'template-generator.py', '--tf', file.name])
            
            #     output_template_dir = 'AWS/EKS/output-template'
            #     os.chdir(output_template_dir)
            #     print("New dir is: ", output_template_dir)
            
            #     subprocess.run(['terraform', 'init'])
            #     subprocess.run(['terraform', 'plan'])
            # elif file.name == 'ebs_volume.yaml':
            #     print("This module is in progress")
            #     subprocess.run(['python3', 'template-generator.py', '--tf', file.name])
            
            #     output_template_dir = 'AWS/EBS/output-template'
            #     os.chdir(output_template_dir)
            #     print("New dir is: ", output_template_dir)
                
            #     subprocess.run(['terraform', 'init'])
            #     subprocess.run(['terraform', 'plan'])
            # elif file.name == 's3.yaml':
            #     print("This module is in progress")
            #     subprocess.run(['python3', 'template-generator.py', '--tf', file.name])
            
            #     output_template_dir = 'AWS/S3/output-template'
            #     os.chdir(output_template_dir)
            #     print("New dir is: ", output_template_dir)
                
            #     subprocess.run(['terraform', 'init'])
            #     subprocess.run(['terraform', 'plan'])
            # elif file.name == 'api_gateway.yaml':
            #     print("This module is in progress")
            #     subprocess.run(['python3', 'template-generator.py', '--tf', file.name])
            
            #     output_template_dir = 'AWS/API-Gateway/output-template'
            #     os.chdir(output_template_dir)
            #     print("New dir is: ", output_template_dir)
                
            #     subprocess.run(['terraform', 'init'])
            #     subprocess.run(['terraform', 'plan'])
            # elif file.name == 'route53.yaml':
            #     print("This module is in progress")
            #     subprocess.run(['python3', 'template-generator.py', '--tf', file.name])
            
            #     output_template_dir = 'AWS/Route53/output-template'
            #     os.chdir(output_template_dir)
            #     print("New dir is: ", output_template_dir)
                
            #     subprocess.run(['terraform', 'init'])
            #     subprocess.run(['terraform', 'plan'])
            # elif file.name == 'vpc.yaml':
            #     print("This module is in progress")
            #     subprocess.run(['python3', 'template-generator.py', '--tf', file.name])
            
            #     output_template_dir = 'AWS/VPC/output-template'
            #     os.chdir(output_template_dir)
            #     print("New dir is: ", output_template_dir)
                
            #     subprocess.run(['terraform', 'init'])
            #     subprocess.run(['terraform', 'plan'])
        elif param_type == 'rbac':
            click.echo("This feature future will be available soon")


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
def delete(type, product, version):
    if type == 'operator' and product == 'nginx':
        print(f'Deleting NGINX with {version} version')
        repo_dir = 'nginx-ingress-helm-operator'
        os.chdir(repo_dir)
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
