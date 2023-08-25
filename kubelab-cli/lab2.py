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

CREDENTIALS_DIR = 'credentials'
LOGS_DIR = 'logs'
GENERIC_LOG_FILE = 'kubelab.log'

AWS_PROVIDER = 'AWS'
AWS_PROFILE_FILE = '~/.aws/credentials'
AWS_LOG_FILE = 'kubelab-aws.log'

AZURE_PROVIDER = 'Azure'
AZURE_PROFILE_FILE = '~/.azure/azureProfile.json'
AZURE_LOG_FILE = 'kubelab-azure.log'

GCP_PROVIDER = 'GCP'
GCP_PROFILE_FILE = '~/.config/gcloud/configurations/config_default'
GCP_LOG_FILE = 'kubelab-gcp.log'

# Get the script dir + create credentials and logs dirs + init files
script_dir = os.path.dirname(os.path.realpath(__file__))
credentials_dir = os.makedirs(os.path.join(script_dir, CREDENTIALS_DIR), exist_ok=True)
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
    global aws_logs_file
    global azure_logs_file
    global gcp_logs_file
    global generic_logs_file
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

def init_terraform(provider, credentials_file):
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
        except subprocess.CalledProcessError as e:
            # Log failure and display error message
            log(f"Terraform for {provider} failed to initialize.", provider)
            log(e.output, provider)
    else:
        log(f"{provider} credentials file not found. Please configure {provider} CLI before proceeding.", provider)

def init_aws():
    aws_credentials_file = os.path.expanduser(AWS_PROFILE_FILE)

    try:
        # Checking if AWS CLI is installed
        subprocess.check_output(['aws', '--version'], stderr=subprocess.STDOUT, universal_newlines=True)
    except subprocess.CalledProcessError as e:
        log("AWS CLI is not installed or configured. Please install and configure it before proceeding.", AWS_PROVIDER)
        log(e.output, AWS_PROVIDER)
    else:
        init_terraform(AWS_PROVIDER, aws_credentials_file)

def init_azure():
    azure_profile_file = os.path.expanduser(AZURE_PROFILE_FILE)

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
            init_terraform(AZURE_PROVIDER, azure_profile_file)

def init_gcp():
    gcp_profile_file = os.path.expanduser(GCP_PROFILE_FILE)

    try:
        # Check if GCP CLI is installed
        subprocess.check_output(['gcloud', '--version'], stderr=subprocess.STDOUT, universal_newlines=True)
    except subprocess.CalledProcessError as e:
        log("Google Cloud CLI is not installed or configured. Please install and configure it before proceeding.", GCP_PROVIDER)
        log(e.output, GCP_PROVIDER)
    else:
        init_terraform(GCP_PROVIDER, gcp_profile_file)


@cli.command()
@click.argument('providers', nargs=-1, type=click.Choice(['aws', 'azure', 'gcp']), required=False)
def init(providers):
    """
    Initializes the credentials needed for the supported cloud providers and Terraform.
    It saves the credentials in the 'credentials' directory and init logs in the 'logs' directory.
    """

    # Init cloud providers
    if not providers or 'aws' in providers:
        init_aws()
    if not providers or 'azure' in providers:
        init_azure()
    if not providers or 'gcp' in providers:
        init_gcp()


@cli.command()
def info():
    """
    Query your cluster for information via an interactive shell from Mondoo.
    """
    print("Information about your cluster coming from the cnquery lib - thanks Mondoo")
    subprocess.run(['cnquery', 'shell', 'k8s'])


if __name__ == '__main__':
    cli()
