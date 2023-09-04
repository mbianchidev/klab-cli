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

UNSUPPORTED_TYPE_MSG = "Unsupported type specified. Only 'cluster' is supported."
UNSUPPORTED_PROVIDER_MSG = "Unsupported provider specified."

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


def check_parameters(**kwargs):
    for param_name, param_value in kwargs.items():
        if param_value is None or param_value == "":
            raise ValueError(f"Parameter '{param_name}' is None or blank. Please check the required parameters and try again.")


def execute_command(command, log_file_path, wait=False):
    with open(log_file_path, 'a') as log_file:
        # Utility function to run a command and wait for its completion
        try:
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

            if wait:
                log(f"Running the {command} in foreground.")
                process.wait()
                # return output
                return process.stdout.read()
            else:
                log(f"Running the {command} in background.")
        # Catching exceptions and raising them
        except subprocess.CalledProcessError as e:
            log(f"Error occurred during {command}. Please check the command and try again. {e}")
            raise e(process.returncode, command)


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
            os.chdir(script_dir)
            os.chdir(f'../providers/{provider}')
            # Initialize Terraform
            subprocess.check_call(['terraform', 'init'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            log(f"Terraform for {provider} is successfully initialized.", provider)
            os.chdir(script_dir)
        except subprocess.CalledProcessError as e:
            # Log failure and display error message
            log(f"Terraform for {provider} failed to initialize. {e}", provider)
            log(e.output, provider)
            os.chdir(script_dir)
    else:
        log(f"{provider} credentials file not found. Please configure {provider} CLI before proceeding.", provider)


def aws_init():
    credentials_file = os.path.expanduser(AWS_PROFILE_FILE)

    try:
        # Checking if AWS CLI is installed
        subprocess.check_output(['aws', '--version'], stderr=subprocess.STDOUT, universal_newlines=True)
    except subprocess.CalledProcessError as e:
        log(f"AWS CLI is not installed or configured. Please install and configure it before proceeding. {e}", AWS_PROVIDER)
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
            log(f"Azure CLI is not logged in. Please log in before proceeding. {e}", AZURE_PROVIDER)
        else:
            terraform_init(AZURE_PROVIDER, credentials_file)


def gcp_init():
    credentials_file = os.path.expanduser(GCP_PROFILE_FILE)

    try:
        # Check if GCP CLI is installed
        subprocess.check_output(['gcloud', '--version'], stderr=subprocess.STDOUT, universal_newlines=True)
    except subprocess.CalledProcessError as e:
        log(f"Google Cloud CLI is not installed or configured. Please install and configure it before proceeding. {e}", GCP_PROVIDER)
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
    return


def extract_default_value(config_file, section, key):

    # Extracts the default section[key] value from the config file or throw an error if it does not exist
    if not os.path.isfile(config_file):
        print(f"The configuration file ({config_file}) does not exist.")
        return

    config = configparser.ConfigParser()
    config.read(config_file)

    # Check if the section exists
    if section in config:
        if key in config[section]:
            return config[section][key]
        else:
            log(f"The {key} key does not exist in the {section} section of the {config_file} file.")
            return
    else:
        log(f"The {section} section does not exist in the {config_file} file.")
        return


def create_eks(cluster_name, region, wait):

    # Extracting the default region from the AWS config file in case it is not set
    if not region:
        log("Region was not set and it is required for AWS. Trying to extract the default value from the AWS config file.")
        region = extract_default_value(aws_config_file, 'default', 'region')

    # Initializing, planning and applying the Terraform configuration for EKS
    os.chdir(script_dir)
    os.chdir(f'../providers/{AWS_PROVIDER}')
    # FIXME backend-config checks
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
    os.chdir(script_dir)
    os.chdir(f'../providers/{AZURE_PROVIDER}')
    # FIXME backend-config checks blob?
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
    os.chdir(script_dir)
    os.chdir(f'../providers/{GCP_PROVIDER}')
    # FIXME backend-config checks bucket?
    execute_command(f'terraform init -backend-config="bucket={cluster_name}-terraform-state" -backend-config="prefix=terraform.tfstate" -backend-config="region={region}"', gcp_logs_file, wait)
    execute_command(f'terraform plan -var="cluster_name={cluster_name}" -var="region={region}" -var="project={project}"', gcp_logs_file, wait)
    execute_command('terraform apply -auto-approve', gcp_logs_file, wait)
    os.chdir(script_dir)
    log(f"GKE Cluster {cluster_name} has been successfully created in {region}.", GCP_PROVIDER)


def get_cluster_info(cluster_name):
    # Getting cluster info from the YAML file if exists
    cluster_file_path = f'{CLUSTERS_DIR}/{cluster_name}_cluster.yaml'
    if not os.path.isfile(cluster_file_path):
        log(f"Cluster configuration file for {cluster_name} not found. Assuming the cluster does not exist or it is not imported yet.")
        return None
    with open(cluster_file_path, 'r') as file:
        cluster_info = yaml.safe_load(file)
    if not cluster_info:
        log(f"Cluster configuration file for {cluster_name} is empty. Please check the file.")
        return None
    return cluster_info

def save_cluster_info(cluster_name, provider, region, resource_group, project, credential_file, products=None):

    # Define the cluster information dictionary
    cluster_info = {
        "name": cluster_name,
        "provider": provider,
        "region": region,
        "credential_file": f"{CREDENTIALS_DIR}/{credential_file}",
        "resource_group": resource_group,
        "project": project,
        "products": products
    }

    # Define the file name based on the cluster name
    file_name = f"{CLUSTERS_DIR}/{cluster_name}_cluster.yaml"

    # Save the cluster information to the YAML file
    with open(file_name, "w") as yaml_file:
        yaml.dump(cluster_info, yaml_file, default_flow_style=False)

    log(f"Cluster information saved to {file_name}.")


@cli.command()
@click.argument('type', type=click.Choice(['cluster']))
@click.option('--name', '-n', required=True, help='Name of the resource to be created', metavar='<resource_name>')
@click.option('--provider', '-p', required=True, type=click.Choice([AWS_PROVIDER, AZURE_PROVIDER, GCP_PROVIDER]), help='Provider of choice', metavar='<provider>')
@click.option('--region', '-r', required=True, type=click.STRING, help='Resource region', metavar='<region>')
@click.option('--resource-group', '-g', type=click.STRING, help='Resource group name (required for Azure)', metavar='<resource_group>')
@click.option('--project', '-p', type=click.STRING, help='Project ID (required for GCP)', metavar='<project_id>')
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
            check_parameters(name=cluster_name, provider=provider, region=region)
            # Check if the cluster already exists
            if len(search_clusters(cluster_name, provider)) > 0:
                log(f"Cluster {cluster_name} already exists, name must be unieuq. Please use a different name.")
                return
            # Creating clusters
            if provider == AWS_PROVIDER:
                create_eks(cluster_name, region, wait)
            if provider == AZURE_PROVIDER:
                check_parameters(resource_group=resource_group)
                create_aks(cluster_name, region, resource_group, wait)
            if provider == GCP_PROVIDER:
                check_parameters(project=project)
                create_gke(cluster_name, region, project, wait)
            else:
                log(UNSUPPORTED_PROVIDER_MSG)
                return
            # Save cluster info
            save_cluster_info(cluster_name, provider, region, resource_group, project, f"{provider}_kube_credential")
            log(f"Cluster {cluster_name} has been successfully created.", provider)
            return
        # Default case
        case _:
            log(UNSUPPORTED_TYPE_MSG)
            return


def search_clusters(name, provider):
    # Search for clusters based on the name and provider
    clusters = []
    for file in os.listdir(CLUSTERS_DIR):
        # Name is optional so if it is not set, all clusters will be considered
        if name is None or fnmatch.fnmatch(file, f'{name}_cluster.yaml'):
            with open(os.path.join(CLUSTERS_DIR, file), 'r') as cluster_file:
                cluster_info = yaml.safe_load(cluster_file)
                # Cluster provider is optional, so if it is not set, all providers will be considered
                if provider is None or provider == cluster_info['provider']:
                    clusters.append(cluster_info)
    return clusters


@cli.command()
@click.argument('type', type=click.Choice(['cluster']))
@click.option('--provider', '-p', required=False, type=click.Choice([AWS_PROVIDER, AZURE_PROVIDER, GCP_PROVIDER]), help='Provider filter', metavar='<provider>')
@click.option('--name', '-n', type=click.STRING, required=False, help='Name filter for resource', metavar='<name>')
def list(type, provider, name):
    """
    Lists resources available and connected to the kubelab cli.

    :param type: the resource type to be listed
    :param provider: the cloud provider to be used for filtering (optional)
    :param name: the name pattern to be used for filtering (optional)
    """

    match type:
        case 'cluster':
            clusters = search_clusters(name, provider)
            if len(clusters) == 0:
                log("No clusters found.")
            else:
                log(f"{clusters}")
            return
        case _:
            log(UNSUPPORTED_TYPE_MSG)
            return

def switch_to_cluster(name, provider, region, resource_group, project):
    check_parameters(name=name, provider=provider)
    # Update the Kubernetes configuration based on the cluster's cloud provider
    if provider == AWS_PROVIDER:
        check_parameters(region=region)
        update_kubeconfig_cmd = f"aws eks update-kubeconfig --region {region} --name {name}"
    if provider == AZURE_PROVIDER:
        check_parameters(resource_group=resource_group)
        update_kubeconfig_cmd = f"az aks get-credentials --resource-group {resource_group} --name {name} --overwrite-existing"
    if provider == GCP_PROVIDER:
        check_parameters(region=region, project=project)
        update_kubeconfig_cmd = f"gcloud container clusters get-credentials {name} --region {region} --project {project}"
    else:
        log(UNSUPPORTED_PROVIDER_MSG)
        return
    execute_command(update_kubeconfig_cmd, generic_logs_file, wait=True)
    log(f"Kubernetes configuration updated for {name} cluster.", provider)
    return

@cli.command()
@click.argument('type', type=click.Choice(['cluster']))
@click.option('--name', '-n', required=True, help='Name of the resource to be used', metavar='<resource_name>')
@click.option('--provider', '-p', required=False, type=click.Choice([AWS_PROVIDER, AZURE_PROVIDER, GCP_PROVIDER]), help='Provider of choice', metavar='<provider>')
@click.option('--region', '-r', required=False, type=click.STRING, help='Resource region', metavar='<region>')
@click.option('--resource-group', '-g', required=False, type=click.STRING, help='Resource group name', metavar='<resource_group>')
@click.option('--project', '-p', required=False, type=click.STRING, help='Project ID', metavar='<project_id>')
def use(type, name, provider, region, resource_group, project):
    """
    Select a resource to switch to, it can be pre-existing or created with the kubelab cli.

    :param type: the type of resource to switch to
    :param cluster: the name of the resource to switch to
    :param provider: the cloud provider of the resource
    :param region: the region of the resource
    :param resource_group: the resource group of the cluster (Azure)
    :param project: the GCP project of the cluster (GCP)
    """
    match type:
        case 'cluster':
            # Check if the cluster already exists and is managed by the kubelab cli
            cluster_info = get_cluster_info(name)
            if not cluster_info:
                log(f"Cluster {name} is not managed by the kubelab-cli. Trying to use it via provided parameters...")
                switch_to_cluster(name, provider, region, resource_group, project)
                # Save cluster info since it is not managed by the kubelab-cli, next time it will be used via the saved info
                save_cluster_info(name, provider, region, resource_group, project, f"{provider}_kube_credential")
                return
            # Extract cluster information from file in case it exists
            cluster_name = cluster_info.get('name')
            cluster_provider = cluster_info.get('provider')
            cluster_region = cluster_info.get('region')
            cluster_resource_group = cluster_info.get('resource_group')
            cluster_project = cluster_info.get('project')
            # Switches to cluster
            switch_to_cluster(cluster_name, cluster_provider, cluster_region, cluster_resource_group, cluster_project)
            return
        case _:
            log(UNSUPPORTED_TYPE_MSG)
            return


def destroy_eks(name, region):
    log(f"You have selected to destroy cluster: {name} that is located in: {region}", AWS_PROVIDER)
    execute_command(f"aws eks describe-cluster --name {name} --region {region}", aws_logs_file, wait=True)
    # Deleting nodegroups via aws cli
    check_output = execute_command(f"aws eks list-nodegroups --cluster-name {name} --region {region}", aws_logs_file, wait=True)
    node_groups = json.loads(check_output)['nodegroups']
    if node_groups:
        for node_group in node_groups:
            log(f"Node group {node_group} is being destroyed...", AWS_PROVIDER)
            execute_command(
                f"aws eks delete-nodegroup --cluster-name {name} --nodegroup-name {node_group} --region {region}",
                aws_logs_file,
                wait=False
            )
    # Deleting cluster
    log(f"The EKS cluster {name} in region {region} is being destroyed...", AWS_PROVIDER)
    execute_command(f"aws eks delete-cluster --name {name} --region {region}", aws_logs_file, wait=True)
    # Deleting connected resources
    os.chdir(script_dir)
    os.chdir(f'../providers/${AWS_PROVIDER}')
    execute_command(f'terraform destroy -auto-approve -var="cluster_name={name}" -var="region={region}"', aws_logs_file, wait=True)
    log("The rest of the resources were also destroyed...", AWS_PROVIDER)
    os.chdir(script_dir)

def destroy_aks(name, region, resource_group):
    log(f"You have selected to destroy cluster: {resource_group}.{name} that is located in: {region}", AZURE_PROVIDER)
    execute_command(f"az aks show -n {name} -g {resource_group} --query provisioningState --output tsv", azure_logs_file, wait=True)
    # Deleting nodepools via az
    nodepool_output = execute_command(
        f"az aks nodepool list --cluster-name {name} -g {resource_group} --query [].name --output tsv",
        azure_logs_file,
        wait=True
    )
    nodepools = nodepool_output.decode().strip().split()
    if nodepools:
        for nodepool in nodepools:
            log(f"Nodepool {nodepool} is being destroyed...", AZURE_PROVIDER)
            execute_command(
                f"az aks nodepool delete --cluster-name {name} -g {resource_group} -n {nodepool} --no-wait",
                azure_logs_file,
                wait=False
            )
    # Deleting cluster via az
    log(f"The AKS cluster {resource_group}.{name} in region {region} is being destroyed...", AZURE_PROVIDER)
    execute_command(f"az aks delete --name {name} --g {resource_group} --yes --no-wait", azure_logs_file, wait=False)
    # Deleting connected resources via Terraform
    os.chdir(script_dir)
    os.chdir(f'../providers/${AZURE_PROVIDER}')
    execute_command(
        f'terraform destroy -auto-approve -var="cluster_name={name}" -var="location={region}" -var="resource_group={resource_group}"',
        azure_logs_file,
        wait=True
    )
    log("The rest of the resources were also destroyed...", AZURE_PROVIDER)
    os.chdir(script_dir)

def destroy_gke(name, region, project, yes):
    log(f"You have selected to destroy cluster: {project}.{name} that is located in: {region}", GCP_PROVIDER)
    execute_command(f"gcloud container clusters describe {name} --region {region} --project {project}", gcp_logs_file, wait=True)
    # Deleting nodes via gcloud
    node_output = execute_command(f'gcloud container node-pools list --cluster {name}', gcp_logs_file, wait=True)
    nodes = node_output.decode().strip().split()
    if nodes:
        for node in nodes:
            log(f"Node {node} is being destroyed...", GCP_PROVIDER)
            execute_command(f"gcloud container node-pools delete {node} --cluster {name} -q", gcp_logs_file, wait=False)
    # Deleting cluster via gcloud
    log(f"The GKE cluster {project}.{name} in region {region} is being destroyed...", GCP_PROVIDER)
    execute_command(f"gcloud container clusters delete {name} --region {region} --project {project} --async", gcp_logs_file, wait=False)
    # Deleting connected resources via Terraform
    os.chdir(script_dir)
    os.chdir(f'../providers/${GCP_PROVIDER}')
    execute_command(
        f'terraform destroy -auto-approve -var="cluster_name={name}" -var="region={region}" -var="project={project}"',
        gcp_logs_file,
        wait=True
    )
    log("The rest of the resources were also destroyed...", GCP_PROVIDER)
    os.chdir(script_dir)


@cli.command()
@click.argument('type', type=click.Choice(['cluster']))
@click.option('--name', '-n', required=True, type=click.STRING, help='Name of the resource to be destroyed', metavar='<resource_name>')
@click.option('--region', required=True, type=click.STRING, help='Location of the resource', metavar='<region>')
@click.option('--interactive', '-i', is_flag=True, help='Shows a list of resources to choose from')
@click.option('--yes', '-y', is_flag=True, help='Skip all prompts and proceed with destruction in quiet mode.')
def destroy(type, name, region, interactive, yes):
    """
    Destroys a resource in the specified cloud provider.

    :param type: the resource type to be destroyed
    :param name: the name of the resource to be destroyed
    :param region: the region where the resource will be destroyed
    :param yes: flag to automatically answer "yes" to all prompts and proceed with destruction
    """
    match type:
        case 'cluster':
            if interactive:
                # List available clusters
                clusters = search_clusters(None, None)
                if not clusters:
                    log("No clusters found.")
                    return

                print("Select a cluster to delete:")
                for i, cluster in enumerate(clusters, start=1):
                    print(f"{i}) {cluster['name']} [{cluster['provider']}, {cluster['region']}]")

                try:
                    selected_index = int(input("Enter the number of the cluster to delete: ")) - 1
                    selected_cluster = clusters[selected_index]
                    cluster_name = selected_cluster['name']
                    cluster_region = selected_cluster['region']
                except (ValueError, IndexError):
                    log("Invalid selection. Aborting.")
                    return
            else:
                check_parameters(name=name, region=region)
                # Use provided parameters
                cluster_name = name
                cluster_region = region
            if not yes:
                # If not in quiet mode, ask for confirmation and in case of positive answer, proceed with destruction
                if not click.confirm("Are you sure you want to destroy the cluster? This operation will also destroy all the resources associated with it. Type 'yes' or 'y' to confirm."):
                    log("Cluster destruction has been cancelled.")
                    return
            cluster_info = get_cluster_info(cluster_name)
            # Extract cluster information
            cluster_name = cluster_info.get('name')
            provider = cluster_info.get('provider')
            cluster_region = cluster_info.get('region')
            resource_group = cluster_info.get('resource_group')
            project = cluster_info.get('project')
            # Validate if the cluster information matches the provided parameters
            if cluster_region != region:
                log(f"Cluster {name} is not in {region} but in {cluster_region} instead. Please specify the correct region.")
                return
            # Destroying clusters
            if provider == AWS_PROVIDER:
                destroy_eks(cluster_name, cluster_region)
            if provider == AZURE_PROVIDER:
                destroy_aks(cluster_name, cluster_region, resource_group)
            if provider == GCP_PROVIDER:
                destroy_gke(cluster_name, cluster_region, project)
            else:
                log(UNSUPPORTED_PROVIDER_MSG)
                return
            # Deleting cluster info file
            os.remove(f"{CLUSTERS_DIR}/{cluster_name}_cluster.yaml")
            log(f"Cluster {cluster_name} has been successfully deleted along with its config file.", provider)
            return
        # Default case
        case _:
            log(UNSUPPORTED_TYPE_MSG)
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
