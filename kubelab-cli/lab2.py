#!/usr/bin/env python3

import click
import os
import subprocess
import json
from deploy import Deploy
import shutil
import fnmatch
import yaml
from datetime import datetime
import configparser

CREDENTIALS_DIR = 'credentials'
LOGS_DIR = 'logs'
CLUSTERS_DIR = 'clusters'
GENERIC_LOG_FILE = 'kubelab.log'

AWS_PROVIDER = 'AWS'
AWS_PROFILE_FILE = '~/.aws/credentials'
AWS_CONFIG_FILE = '~/.aws/config'
AWS_LOG_FILE = 'kubelab-aws.log'

AZURE_PROVIDER = 'Azure'
AZURE_PROFILE_FILE = '~/.azure/azureProfile.json'
AZURE_CONFIG_FILE = '~/.azure/config'
AZURE_LOG_FILE = 'kubelab-azure.log'

GCP_PROVIDER = 'GCP'
GCP_PROFILE_FILE = '~/.config/gcloud/configurations/config_default'
GCP_CONFIG_FILE = '~/.config/gcloud/configurations/config_default'
GCP_LOG_FILE = 'kubelab-gcp.log'

# Get the script dir + create credentials and logs dirs + init files
script_dir = os.path.dirname(os.path.realpath(__file__))

credentials_dir = os.makedirs(os.path.join(script_dir, CREDENTIALS_DIR), exist_ok=True)
aws_credentials_file = os.path.join(credentials_dir, f"{AWS_PROVIDER}_kube_credential")
azure_credentials_file = os.path.join(credentials_dir, f"{AZURE_PROVIDER}_kube_credential")
gcp_credentials_file = os.path.join(credentials_dir, f"{GCP_PROVIDER}_kube_credential")

aws_config_file = os.path.expanduser(AWS_CONFIG_FILE)
azure_config_file = os.path.expanduser(AZURE_CONFIG_FILE)
gcp_config_file = os.path.expanduser(GCP_CONFIG_FILE)

logs_dir = os.makedirs(os.path.join(script_dir, LOGS_DIR), exist_ok=True)
aws_logs_file = os.path.join(logs_dir, AWS_LOG_FILE)
azure_logs_file = os.path.join(logs_dir, AZURE_LOG_FILE)
gcp_logs_file = os.path.join(logs_dir, GCP_LOG_FILE)
generic_logs_file = os.path.join(logs_dir, GENERIC_LOG_FILE)

@click.group()
@click.version_option()
def cli():
    pass


def log(message, provider=None):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    if provider == AWS_PROVIDER:
        log_file = aws_logs_file
    elif provider == AZURE_PROVIDER:
        log_file = azure_logs_file
    elif provider == GCP_PROVIDER:
        log_file = gcp_logs_file
    else:
        log_file = generic_logs_file
    click.echo(log_entry)
    with open(log_file, 'a') as log_file:
        log_file.write(log_entry)


def execute_command(command, log_file_path, wait=False):
    with open(log_file_path, 'a') as log_file:
        # Utility function to run a command and wait for its completion
        process = subprocess.Popen(
            command,
            shell=True,
            text=True,
            stdout=log_file,
            stderr=subprocess.STDOUT
        )

        # if process is in error state, wait for it to finish and raise an exception
        if process.poll() is not None and process.returncode != 0:
            process.wait()
            log(f"Error running the {command}.")
            raise subprocess.CalledProcessError(process.returncode, command)

        if wait:
            log(f"Running the {command} in foreground.")
            process.wait()
        else:
            log(f"Running the {command} in background.")


def terraform_init(provider, credentials_file):
    global credentials_dir
    # Check if the credentials file exists
    if os.path.isfile(credentials_file):
        kube_credentials_file = os.path.join(credentials_dir, f'{provider}_kube_credential')

        # Copy credentials to kube_credentials_file_path
        shutil.copy(credentials_file, kube_credentials_file)
        log(f'{provider} credentials saved to {kube_credentials_file}\n')
        log(f"Initializing Terraform for {provider}...\n")

        try:
            # Change directory to the provider-specific directory
            os.chdir(f'../providers/{provider}')

            # Initialize Terraform
            subprocess.check_call(['terraform', 'init'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

            # Log success
            log(f"Terraform for {provider} is successfully initialized.", provider)

            # Change directory back to the script directory
            os.chdir(script_dir)
        except subprocess.CalledProcessError as e:
            # Log failure and display error message
            log(f"Terraform for {provider} failed to initialize.", provider)
            log(e.output, provider)
    else:
        log(f"{provider} credentials file not found. Please configure {provider} CLI before proceeding.", provider)


def aws_init():
    credentials_file = os.path.expanduser(AWS_PROFILE_FILE)

    try:
        # Checking if AWS CLI is installed
        subprocess.check_output(['aws', '--version'], stderr=subprocess.STDOUT, universal_newlines=True)
    except subprocess.CalledProcessError as e:
        log("AWS CLI is not installed or configured. Please install and configure it before proceeding.", AWS_PROVIDER)
        log(e.output, AWS_PROVIDER)
    else:
        terraform_init(AWS_PROVIDER, credentials_file)


def azure_init():
    credentials_file = os.path.expanduser(AZURE_PROFILE_FILE)

    try:
        # Check if Azure CLI is installed
        subprocess.check_output(['az', '--version'], stderr=subprocess.STDOUT, universal_newlines=True)
    except subprocess.CalledProcessError as e:
        log("Azure CLI is not installed or configured. Please install and configure it before proceeding.", AZURE_PROVIDER)
        log(e.output, AZURE_PROVIDER)
    else:
        try:
            # Check if Azure CLI is logged in
            subprocess.check_output(['az', 'account', 'show'], stderr=subprocess.STDOUT, universal_newlines=True)
        except subprocess.CalledProcessError as e:
            log("Azure CLI is not logged in. Please log in before proceeding.", AZURE_PROVIDER)
        else:
            terraform_init(AZURE_PROVIDER, credentials_file)


def gcp_init():
    credentials_file = os.path.expanduser(GCP_PROFILE_FILE)

    try:
        # Check if GCP CLI is installed
        subprocess.check_output(['gcloud', '--version'], stderr=subprocess.STDOUT, universal_newlines=True)
    except subprocess.CalledProcessError as e:
        log("Google Cloud CLI is not installed or configured. Please install and configure it before proceeding.", GCP_PROVIDER)
        log(e.output, GCP_PROVIDER)
    else:
        terraform_init(GCP_PROVIDER, credentials_file)


@cli.command()
@click.argument('providers', nargs=-1, type=click.Choice([AWS_PROVIDER, AZURE_PROVIDER, GCP_PROVIDER]), required=False)
def init(providers):
    """
    Initializes the credentials needed for the supported cloud providers and Terraform.
    It saves the credentials in the 'credentials' directory and init logs in the 'logs' directory.
    """

    # Init cloud providers
    if not providers or AWS_PROVIDER in providers:
        aws_init()
    if not providers or AZURE_PROVIDER in providers:
        azure_init()
    if not providers or GCP_PROVIDER in providers:
        gcp_init()

def extract_default_value(config_file, section, key):

    # Extracts the default section[key] value from the config file or throw an error if it does not exist
    if not os.path.isfile(config_file):
        print(f"The configuration file ({config_file}) does not exist.")
        exit(1)

    config = configparser.ConfigParser()
    config.read(config_file)

    # Check if the section exists
    if section in config:
        if key in config[section]:
            return config[section][key]
        else:
            log(f"The {key} key does not exist in the {section} section of the {config_file} file.")
            exit(1)
    else:
        log(f"The {section} section does not exist in the {config_file} file.")
        exit(1)

def create_eks(cluster_name, region, wait):

    # Extracting the default region from the AWS config file in case it is not set
    if not region:
        log("Region was not set and it is required for AWS. Trying to extract the default value from the AWS config file.")
        region = extract_default_value(aws_config_file, 'default', 'region')

    # Initializing, planning and applying the Terraform configuration for EKS
    os.chdir(f'../providers/{AWS_PROVIDER}')
    execute_command(f'terraform init -backend-config="bucket={cluster_name}-terraform-state" -backend-config="key=terraform.tfstate" -backend-config="region={region}"', aws_logs_file, wait)
    execute_command(f'terraform plan -var="cluster_name={cluster_name}" -var="region={region}"', aws_logs_file, wait)
    execute_command('terraform apply -auto-approve', aws_logs_file, wait)
    os.chdir(script_dir)
    log(f"EKS Cluster {cluster_name} has been successfully created in {region}.", AWS_PROVIDER)

def create_aks(cluster_name, region, resource_group, wait):

    # Extracting the default region and resource group from the Azure config file in case they are not set
    if not region:
        log("Region was not set and it is required for Azure. Trying to extract the default value from the Azure config file.")
        region = extract_default_value(azure_config_file, 'defaults', 'location')
    if not resource_group:
        log("Resource Group was not set and it is required for Azure. Trying to extract the default value from the Azure config file.")
        resource_group = extract_default_value(azure_config_file, 'defaults', 'group')

    # Initializing, planning and applying the Terraform configuration for AKS
    os.chdir(f'../providers/{AZURE_PROVIDER}')
    execute_command(f'terraform init -backend-config="blob={cluster_name}-terraform-state" -backend-config="key=terraform.tfstate" -backend-config="region={region}"', azure_logs_file, wait)
    execute_command(f'terraform plan -var="cluster_name={cluster_name}" -var="region={region}" -var="resource_group={resource_group}"', azure_logs_file, wait)
    execute_command('terraform apply -auto-approve', azure_logs_file, wait)
    os.chdir(script_dir)
    log(f"AKS Cluster {cluster_name} has been successfully created in {region}.", AZURE_PROVIDER)

def create_gke(cluster_name, region, project, wait):

    # Extracting the default region and project from the GCP config file in case they are not set
    if not region:
        log("Region was not set and it is required for GCP. Trying to extract the default value from the GCP config file.")
        region = extract_default_value(gcp_config_file, 'compute', 'region')
    if not project:
        log("Project was not set and it is required for GCP. Trying to extract the default value from the GCP config file.")
        project = extract_default_value(gcp_config_file, 'core', 'project')

    # Initializing, planning and applying the Terraform configuration for GKE
    os.chdir(f'../providers/{GCP_PROVIDER}')
    execute_command(f'terraform init -backend-config="bucket={cluster_name}-terraform-state" -backend-config="prefix=terraform.tfstate" -backend-config="region={region}"', gcp_logs_file, wait)
    execute_command(f'terraform plan -var="cluster_name={cluster_name}" -var="region={region}" -var="project={project}"', gcp_logs_file, wait)
    execute_command('terraform apply -auto-approve', gcp_logs_file, wait)
    os.chdir(script_dir)
    log(f"GKE Cluster {cluster_name} has been successfully created in {region}.", GCP_PROVIDER)

def save_cluster_info(cluster_name, provider, region, credential_file, products=None):

    # Define the cluster information dictionary
    cluster_info = {
        "name": cluster_name,
        "provider": provider,
        "region": region,
        "credential_file": f"{CREDENTIALS_DIR}/{credential_file}",
        "products": products
    }

    # Define the file name based on the cluster name
    file_name = f"{CLUSTERS_DIR}/{cluster_name}_cluster.yaml"

    # Save the cluster information to the YAML file
    with open(file_name, "w") as yaml_file:
        yaml.dump(cluster_info, yaml_file, default_flow_style=False)

@cli.command()
@click.argument('type', type=click.Choice(['cluster']))
@click.option('--name', '-n', required=True, help='Name of the cluster to be created', metavar='<cluster_name>')
@click.option('--provider', '-p', required=True, type=click.Choice([AWS_PROVIDER, AZURE_PROVIDER, GCP_PROVIDER]), help='Provider of choice', metavar='<provider>')
@click.option('--region', '-r', required=True, type=str, help='Cluster region (required for AWS and GCP)', metavar='<region>')
@click.option('--resource-group', '-g', type=str, help='Resource group name (required for Azure)', metavar='<resource_group>')
@click.option('--project', '-p', type=str, help='GCP project ID (required for GCP)', metavar='<project_id>')
@click.option('--wait', '-w', is_flag=True, default=False, showDefault=True, help='wait for commands completion or not')
def create(type, cluster_name, provider, region, resource_group, project, wait):
    """
    Creates a k8s cluster in the specified cloud provider.

    :param type: the resource to be created
    :param cluster_name: the name of the cluster to be created (otional)
    :param provider: the cloud provider to be used
    :param region: the region where the resource will be created
    :param resource_group: the resource group where the resource will be created (optional)
    :param project: the GCP project ID where the resource will be created (optional)
    """

    match type:
        case 'cluster':
            if not cluster_name:
                log("Cluster name was not set and it is required. Please specify it as a parameter.")
                return
            # Creating clusters
            if provider == AWS_PROVIDER:
                create_eks(cluster_name, region, wait)
            if provider == AZURE_PROVIDER:
                create_aks(cluster_name, region, resource_group, wait)
            if provider == GCP_PROVIDER:
                create_gke(cluster_name, region, project, wait)
            else:
                log("Invalid provider specified.")
                return
            # Save cluster info
            save_cluster_info(cluster_name, provider, region, f"{provider}_kube_credential")
        # Default case
        case _:
            log("Invalid type specified. Only 'cluster' is supported.")
            return


@cli.command()
def info():
    """
    Query your cluster for information via an interactive shell from Mondoo.
    """
    print("Information about your cluster coming from the cnquery lib - thanks Mondoo")
    subprocess.run(['cnquery', 'shell', 'k8s'])


if __name__ == '__main__':
    cli()
