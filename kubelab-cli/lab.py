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

@click.group()
def cli():
    pass

def log_message(log_file, message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    with open(log_file, 'a') as log_file:
        log_file.write(log_entry)

@cli.command()
def init():
    """
    Initializes the credentials needed for the supported cloud providers and Terraform.
    It saves the credentials in the 'credentials' directory and the logs in the 'logs' directory.
    Usage: lab init
    """
    script_dir = os.path.dirname(os.path.realpath(__file__))
    credentials_dir = os.path.join(script_dir, 'credentials')
    os.makedirs(credentials_dir, exist_ok=True)

    # Create logs directory
    logs_dir = os.path.join(script_dir, 'logs')
    os.makedirs(logs_dir, exist_ok=True)

    # AWS
    aws_credentials_file = os.path.expanduser('~/.aws/credentials')
    try:
        process = subprocess.Popen(['aws', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        stdout_output, stderr_output = process.communicate()
        exit_code = process.wait()
    except FileNotFoundError:
        click.echo('AWS CLI is not installed or configured. Please install and configure it before proceeding.\n')
        aws_logs_file = os.path.join(logs_dir, 'aws_terraform_init.log')
        log_message(aws_logs_file, "AWS CLI is not installed or configured.")
    else:
        if exit_code == 0:
            if os.path.isfile(aws_credentials_file):
                aws_kube_credentials_file = os.path.join(credentials_dir, 'aws_kube_credential')
                shutil.copy(aws_credentials_file, aws_kube_credentials_file)
                click.echo(f'AWS credentials saved to {aws_kube_credentials_file}\n')
                aws_logs_file = os.path.join(logs_dir, 'aws_terraform_init.log')
                log_message(aws_logs_file, "AWS credentials saved.")
                print("Initializing Terraform for AWS...\n")
                os.chdir('../providers/AWS')
                process = subprocess.Popen(['terraform', 'init'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                stderr_output = process.communicate()
                exit_code = process.wait()
                if exit_code == 0:
                    log_message(aws_logs_file, "Terraform for AWS is successfully initialized.")
                    print("Terraform for AWS is successfully initialized.\n")
                else:
                    log_message(aws_logs_file, "Terraform for AWS failed to initialize.")
                    log_message(aws_logs_file, stderr_output)
                    print("Terraform for AWS failed to initialize. Please check the logs in the 'logs' directory.\n")
            else:
                click.echo('AWS credentials file not found. Please configure AWS CLI before proceeding.\n')
                aws_logs_file = os.path.join(logs_dir, 'aws_terraform_init.log')
                log_message(aws_logs_file, "AWS credentials file not found.")
        else:
            click.echo('AWS CLI is not installed or configured. Please install and configure it before proceeding.\n')
            aws_logs_file = os.path.join(logs_dir, 'aws_terraform_init.log')
            log_message(aws_logs_file, "AWS CLI is not installed or configured.")

    # Azure
    try:
        azure_credential_check = subprocess.run(['az', 'account', 'show'], capture_output=True, text=True)
    except FileNotFoundError:
        click.echo('Azure CLI is not installed or configured. Please install and configure it before proceeding.\n')
        azure_logs_file = os.path.join(logs_dir, 'azure_terraform_init.log')
        log_message(azure_logs_file, "Azure CLI is not installed or configured.")
    else:
        if azure_credential_check.returncode == 0:
            output = azure_credential_check.stdout.strip()
            azure_credentials_file = os.path.join(credentials_dir, 'azure_kube_credential')
            with open(azure_credentials_file, 'w') as f:
                f.write(output)
            click.echo(f'Azure credentials saved to {azure_credentials_file}\n')
            azure_logs_file = os.path.join(logs_dir, 'azure_terraform_init.log')
            log_message(azure_logs_file, "Azure credentials saved.")
            print("Initializing Terraform for Azure...")
            os.chdir('../providers/Azure')
            process = subprocess.Popen(['terraform', 'init'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            stdout_output, stderr_output = process.communicate()
            exit_code = process.wait()
            if exit_code == 0:
                log_message(azure_logs_file, "Terraform for Azure is successfully initialized.")
                print("Terraform for Azure is successfully initialized.\n")
            else:
                log_message(azure_logs_file, "Terraform for Azure failed to initialize.")
                log_message(azure_logs_file, stderr_output)
                print("Terraform for Azure failed to initialize. Please check the logs in the 'logs' directory.\n")
        else:
            click.echo('Azure CLI is not logged in. Please log in before proceeding.\n')
            azure_logs_file = os.path.join(logs_dir, 'azure_terraform_init.log')
            log_message(azure_logs_file, "Azure CLI is not logged in.")

    # Google Cloud
    gcloud_credentials_file = os.path.expanduser('~/.config/gcloud/application_default_credentials.json')
    if os.path.isfile(gcloud_credentials_file):
        gcp_kube_credentials_file = os.path.join(credentials_dir, 'gcp_kube_credential')
        shutil.copy(gcloud_credentials_file, gcp_kube_credentials_file)
        click.echo(f'Gcloud credentials saved to {gcp_kube_credentials_file}')
        gcp_logs_file = os.path.join(logs_dir, 'gcp_terraform_init.log')
        log_message(gcp_logs_file, "Gcloud credentials saved.")
        print("Initializing Terraform for Google Cloud...")
        os.chdir('../providers/GCP')
        process = subprocess.Popen(['terraform', 'init'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        stderr_output = process.communicate()
        exit_code = process.wait()
        if exit_code == 0:
            log_message(gcp_logs_file, "Terraform for Google Cloud is successfully initialized.")
            print("Terraform for Google Cloud is successfully initialized.\n")
        else:
            log_message(gcp_logs_file, "Terraform for Google Cloud failed to initialize.")
            log_message(gcp_logs_file, stderr_output)
            print("Terraform for Google Cloud failed to initialize. Please check the logs in the 'logs' directory.\n")
    else:
        click.echo('gcloud CLI is not installed or configured. Please install and configure it before proceeding.\n')
        gcp_logs_file = os.path.join(logs_dir, 'gcp_terraform_init.log')
        log_message(gcp_logs_file, "gcloud CLI is not installed or configured.")


def wait_for_exe(command, log_file_path, wait_for_completion=True):
    """
    Runs a command and waits for its completion.

    :param command: The command to execute.
    :param log_file_path: The path to the log file to store the command output.
    :param wait_for_completion: If True, wait for the process to complete; otherwise, run it in the background.
    """
    with open(log_file_path, 'w') as log_file:
        process = subprocess.Popen(
            command,
            shell=True,
            text=True,
            stdout=log_file,
            stderr=subprocess.STDOUT
        )

        if wait_for_completion:
            process.wait()
        else:
            click.echo("Running the command in the background.")


def create_log_directory_and_file(log_file_path):
    # Create the log directory if it doesn't exist
    if not os.path.exists('log'):
        os.makedirs('log')

    # Create the log file if it doesn't exist
    if not os.path.exists(log_file_path):
        with open(log_file_path, 'w'):
            pass


@cli.command()
@click.argument('type', type=click.Choice(['cluster']))
@click.option('--cluster-name', '-cn', help='Name of the cluster to be created', metavar='<cluster_name>')
@click.option('--provider', '-pr', type=click.Choice(['AWS', 'Azure', 'GCP']), help='Filter clusters by provider')
@click.option('--region', '-r', type=str, help='Cluster region (required for AWS and GCP)', metavar='<region>')
@click.option('--resource-group', '-rg', type=str, help='Resource group name (required for Azure)', metavar='<resource_group>')
@click.option('--project', '-p', type=str, help='GCP project ID (required for GCP)', metavar='<project_id>')
def create(type, cluster_name, provider, region, resource_group, project):
    """
    Creates a k8s cluster in the specified cloud provider.

    :param type: TODO
    :param cluster_name: TODO
    :param provider: TODO
    :param region: TODO
    :param resource_group: TODO
    :param project: TODO
    """
    if type != 'cluster':
        click.echo("Invalid type specified. Only 'cluster' is supported.")
        return

    try:
        if provider == "AWS":

            if not cluster_name:
                cluster_name = "eks"
                click.echo(f"No cluster name set, default cluster name: {cluster_name} will be used.")

            if not region:
                region = "eu-west-2"
                click.echo(f"No region set, default region: {region} will be used.")

            os.chdir('../providers/AWS')

            log_file_path = 'log/kubelab.log'

            create_log_directory_and_file(log_file_path)

            click.echo("Running terraform plan to check the input parameters and Terraform configuration.")
            wait_for_exe(
                f'terraform plan -var="cluster_name={cluster_name}" -var="region={region}"',
                log_file_path
            )

            click.echo("Terraform plan was completed successfully!")

            wait_for_exe(
                f'terraform apply -auto-approve -var="cluster_name={cluster_name}" -var="region={region}"',
                log_file_path,
                wait_for_completion=False
            )

            click.echo("Cluster will be created in 15 minutes and for logs check log/kubelab.log file")

        elif provider == "Azure":
            if not cluster_name:
                cluster_name = "aks"
                click.echo(f"No cluster name set, default cluster name: {cluster_name} will be used.")

            if not resource_group:
                resource_group = "kubelab_resource_group"
                click.echo(f"No resource group set, default resource group: {resource_group} will be used.")

            if not region:
                region = "eastus"
                click.echo(f"No region set, default region: {region} will be used.")

            os.chdir('../providers/Azure')

            log_file_path = 'log/kubelab.log'

            create_log_directory_and_file(log_file_path)

            click.echo("Running terraform plan to check the input parameters and Terraform configuration.")
            wait_for_exe(
                f'terraform plan -var="cluster_name={cluster_name}" -var="resource_group={resource_group}" -var="location={region}"',
                log_file_path
            )

            click.echo("Terraform plan was completed successfully!")

            wait_for_exe(
                f'terraform apply -auto-approve -var="cluster_name={cluster_name}" -var="resource_group={resource_group}" -var="location={region}"',
                log_file_path,
                wait_for_completion=False
            )

            click.echo("Cluster will be created in 15 minutes and for logs check log/kubelab.log file")

        elif provider == "GCP":
            if not cluster_name:
                cluster_name = "gke"
                click.echo(f"No cluster name set, default cluster name: {cluster_name} will be used.")

            if not region:
                region = "europe-central2"
                click.echo(f"No region set, default region: {region} will be used.")

            if not project:
                click.echo("Project ID is required for GCP!")
                click.echo("Make sure to add --project <project-id> or -p <project-id> option.")
                return

            os.chdir('../providers/GCP')

            log_file_path = 'log/kubelab.log'

            create_log_directory_and_file(log_file_path)

            click.echo("Running terraform plan to check the input parameters and Terraform configuration.")
            wait_for_exe(
                f'terraform plan -var="cluster_name={cluster_name}" -var="region={region}" -var="project={project}"',
                log_file_path
            )

            if not os.path.exists('log'):
                os.makedirs('log')

            click.echo("Terraform plan was completed successfully!")

            wait_for_exe(
                f'terraform apply -auto-approve -var="cluster_name={cluster_name}" -var="region={region}" -var="project={project}"',
                log_file_path,
                wait_for_completion=False
            )

            click.echo("Cluster will be created in 15 minutes and for logs check log/kubelab.log file")

        else:
            click.echo("Invalid cloud provider specified!")
            click.echo("Make sure to add --provider <cloud-provider> or -pr <cloud-provider> option.")
            return

        os.chdir('../kubelab-cli')

        # Create cluster_credentials directory if it doesn't exist
        credentials_dir = 'cluster_credentials'
        if not os.path.exists(credentials_dir):
            os.makedirs(credentials_dir)

        # Define cluster_info outside the if-elif blocks
        cluster_info = None

        # Retrieve the credentials file path based on the cloud provider
        if provider == "AWS":
            credentials_file = os.path.join('credentials', 'aws_kube_credential')

            cluster_info = {
                'cluster_credentials': credentials_file,
                'cluster_name': cluster_name,
                'cluster_provider': provider,
                'cluster_region': region
            }
        elif provider == "Azure":
            credentials_file = os.path.join('credentials', 'azure_kube_credential')

            cluster_info = {
                'cluster_credentials': credentials_file,
                'cluster_name': cluster_name,
                'cluster_provider': provider,
                'cluster_region': region,
                'cluster_resource_group': resource_group
            }
        elif provider == "GCP":
            credentials_file = os.path.join('credentials', 'gcp_kube_credential')

            cluster_info = {
                'cluster_credentials': credentials_file,
                'cluster_name': cluster_name,
                'cluster_provider': provider,
                'cluster_region': region,
                'cluster_project': project
            }

        # Check if the cluster name, provider, and region already exist in clusters.yaml
        yaml_file_path = os.path.join(credentials_dir, 'clusters.yaml')
        existing_clusters = []
        if os.path.exists(yaml_file_path):
            with open(yaml_file_path, 'r') as yaml_file:
                existing_clusters = yaml.safe_load(yaml_file)
                existing_clusters = existing_clusters if existing_clusters is not None else []

        existing_clusters_set = {(cluster['cluster_name'], cluster['cluster_provider'], cluster.get('cluster_region', '')) for cluster in existing_clusters}

        if (cluster_name, provider, region) in existing_clusters_set:
            print(f"The cluster with name '{cluster_name}', provider '{provider}', and region '{region}' already exists in clusters.yaml. Skipping append.")
        else:
            existing_clusters.append(cluster_info)
            with open(yaml_file_path, 'w') as yaml_file:
                yaml.dump(existing_clusters, yaml_file)

            print(f"Cluster '{cluster_name}' with provider '{provider}' and region '{region}' is being deployed..")

    except (subprocess.CalledProcessError, KeyError) as e:
        print(f"Error: Failed to retrieve cluster name. {e}")


@cli.command()
@click.argument('type', type=click.Choice(['cluster']))
@click.option('--provider', type=click.Choice(['AWS', 'Azure', 'GCP']), help='Filter clusters by provider')
@click.option('--name', help='Filter clusters by name pattern')
def list(type, provider, name):
    """
    Lists k8s clusters connected in the specified cloud provider.

    :param type: TODO
    :param provider: TODO
    :param name: TODO
    """
    if type == 'cluster':
        credentials_dir = 'cluster_credentials'
        yaml_file_path = os.path.join(credentials_dir, 'clusters.yaml')

        if not os.path.exists(yaml_file_path):
            click.echo("No clusters.yaml file found.")
            return

        with open(yaml_file_path, 'r') as yaml_file:
            clusters = yaml.safe_load(yaml_file)

        if not clusters:
            click.echo("No clusters found.")
            return

        filtered_clusters = []
        for cluster in clusters:
            if provider and cluster.get('cluster_provider') != provider:
                continue
            if name and not fnmatch.fnmatch(cluster.get('cluster_name'), f'*{name}*'):
                continue
            filtered_clusters.append(cluster)

        if not filtered_clusters:
            click.echo("No clusters found matching the specified filter.")
            return

        click.echo("Clusters:")
        for cluster in filtered_clusters:
            click.echo(f"- cluster_name: {cluster['cluster_name']}")
            click.echo(f"  cluster_provider: {cluster['cluster_provider']}")
            click.echo(f"  cluster_region: {cluster['cluster_region']}")
            click.echo(f"  cluster_credentials: {cluster['cluster_credentials']}")
            if 'cluster_resource_group' in cluster:
                click.echo(f"  cluster_resource_group: {cluster['cluster_resource_group']}")
            if 'cluster_project' in cluster:
                click.echo(f"  cluster_project: {cluster['cluster_project']}")
            click.echo()
    else:
        print("You have selected a wrong type, run 'lab list --help' for more information.")


@cli.command()
@click.argument('param_type', type=click.Choice(['cluster']))
@click.option('--name', type=click.STRING, help='What is the cluster named as?')
@click.option('--region', type=click.STRING, help='Where is the cluster located?')
@click.option('--yes', '-y', is_flag=True, help='Automatically answer "yes" to all prompts and proceed with destruction.')
def destroy(param_type, name, region, yes):
    """
    Destroys a k8s cluster in the specified cloud provider.

    :param param_type: TODO
    :param name: TODO
    :param region: TODO
    :param yes: TODO
    """
    if param_type == "cluster":
        if name is None and region is None:
            print("Please provide both the cluster name and region.")
        elif name is None:
            print("Please provide the cluster name.")
        elif region is None:
            print("Please provide the cluster region.")
        else:
            # Load cluster credentials from YAML file
            with open('cluster_credentials/clusters.yaml', 'r') as file:
                data = yaml.safe_load(file)

            # Find the matching cluster based on name and region
            matching_clusters = [cluster for cluster in data if cluster.get('cluster_name') == name and cluster.get('cluster_region') == region]

            if matching_clusters:
                cluster = matching_clusters[0]  # Use the first matching cluster

                cluster_provider = cluster.get('cluster_provider')

                if cluster_provider == "AWS":
                    # Perform AWS-specific destruction command
                    aws_cluster_name = cluster.get('cluster_name')
                    aws_cluster_region = cluster.get('cluster_region')

                    print(f"You have selected to destroy cluster: {aws_cluster_name} that is located in: {aws_cluster_region}")
                    check_command = f"aws eks describe-cluster --name {aws_cluster_name} --region {aws_cluster_region}"
                    try:
                        subprocess.check_output(check_command, stderr=subprocess.STDOUT, shell=True)
                    except subprocess.CalledProcessError as e:
                        if "ResourceNotFoundException" in e.output.decode():
                            print(f"The EKS cluster named {aws_cluster_name} in region {aws_cluster_region} does not exist.")
                        else:
                            print("Error occurred during describe-cluster command. Please check the command and try again.")
                        return

                    if yes:
                        confirmation = 'yes'
                    else:
                        confirmation = input("Are you sure that you want to destroy this cluster? (yes/no): ").lower()
                    if confirmation == 'yes':
                        check_command = f"aws eks list-nodegroups --cluster-name {aws_cluster_name} --region {aws_cluster_region}"

                        try:
                            check_output = subprocess.check_output(check_command, stderr=subprocess.STDOUT, shell=True)
                        except subprocess.CalledProcessError:
                            print("Error occurred during list-nodegroups command. Please check the command and try again.")
                            return

                        if check_output:
                            node_groups = json.loads(check_output)['nodegroups']
                            if node_groups:
                                for node_group in node_groups:
                                    check_command = f"aws eks list-nodegroups --cluster-name {aws_cluster_name} --region {aws_cluster_region}"
                                    delete_node_group_command = f"aws eks delete-nodegroup --cluster-name {aws_cluster_name} --nodegroup-name {node_group} --region {aws_cluster_region}"
                                    print(f"Node group {node_group} is being destroyed..")
                                    subprocess.Popen(delete_node_group_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True).communicate()

                                    while True:
                                        # Run the AWS CLI command to list node groups
                                        check_command = f"aws eks list-nodegroups --cluster-name {aws_cluster_name} --region {aws_cluster_region}"
                                        result = subprocess.run(check_command, shell=True, capture_output=True, text=True)
                                        if result.returncode == 0:
                                            # Parse the JSON output
                                            output = json.loads(result.stdout)
                                            if "nodegroups" in output and len(output["nodegroups"]) == 0:
                                                print(f"The Node Groups of the {aws_cluster_name} cluster have been destroyed.")
                                                break
                                        else:
                                            print("An error occurred while executing the command.")
                        delete_command = f"aws eks delete-cluster --name {aws_cluster_name} --region {aws_cluster_region}"
                        print(f"The EKS cluster {aws_cluster_name} in region {aws_cluster_region} is being destroyed..")
                        subprocess.check_call(delete_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)

                        while True:
                            check_cluster_command = f"aws eks describe-cluster --name {aws_cluster_name} --region {aws_cluster_region}"
                            try:
                                check_output = subprocess.check_output(check_cluster_command, stderr=subprocess.STDOUT, shell=True)
                            except subprocess.CalledProcessError as e:
                                if "ResourceNotFoundException" in e.output.decode():
                                    print(f"The EKS cluster named {aws_cluster_name} in region {aws_cluster_region} has been destroyed.")
                                    break
                                else:
                                    print("Error occurred during describe-cluster command. Please check the command and try again.")
                                    return
                        data.remove(cluster)
                        with open('cluster_credentials/clusters.yaml', 'w') as file:
                            yaml.dump(data, file)
                        if yes:
                            destroy_all = 'yes'
                        else:
                            destroy_all = input("Do you want to destroy all other resources? (yes/no): ").lower()
                        if destroy_all == 'yes':
                            os.chdir('../providers/AWS')
                            destroy_all_command = f'terraform destroy -auto-approve -var="cluster_name={aws_cluster_name}" -var="region={aws_cluster_region}"'
                            process = subprocess.Popen(destroy_all_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True, universal_newlines=True)
                            print("The rest of the resources are being destroyed... ")
                            exit_code = process.wait()
                            if exit_code == 0:
                                print("The rest of the resources are destroyed.")
                            else:
                                print("The destroy of the resources failed")
                        else:
                            print("You choose not to destroy other resources")
                            exit()
                    elif confirmation == 'no':
                        print("The destruction of the cluster has been canceled.")
                    else:
                        print("Invalid response. Please provide a valid response (yes/no).")

                elif cluster_provider == "Azure":
                    azure_cluster_name = cluster.get('cluster_name')
                    azure_resource_group = cluster.get('cluster_resource_group')
                    azure_cluster_region = cluster.get('cluster_region')

                    try:
                        describe_command = f"az aks show --name {azure_cluster_name} --resource-group {azure_resource_group} --query provisioningState --output tsv"
                        result = subprocess.check_output(describe_command, stderr=subprocess.STDOUT, shell=True)
                        provisioning_state = result.decode().strip()

                        if provisioning_state == "Succeeded":
                            print(f"The AKS cluster named {azure_cluster_name} in resource group {azure_resource_group} exists.")
                            try:
                                if yes:
                                    confirmation = 'yes'
                                else:
                                    confirmation = input("Are you sure that you want to destroy this cluster? (yes/no): ").lower()
                                if confirmation == 'yes':
                                    delete_command = f"az aks delete --name {azure_cluster_name} --resource-group {azure_resource_group} --yes"
                                    print(f"Deleting AKS cluster named {azure_cluster_name} in resource group {azure_resource_group}.")
                                    subprocess.check_output(delete_command, stderr=subprocess.STDOUT, shell=True)
                                    print(f"The AKS cluster named {azure_cluster_name} in resource group {azure_resource_group} has been deleted successfully.")
                                    data.remove(cluster)
                                    with open('cluster_credentials/clusters.yaml', 'w') as file:
                                        yaml.dump(data, file)
                                    if yes:
                                        destroy_all = 'yes'
                                    else:
                                        destroy_all = input("Do you want to destroy all other resources? (yes/no): ").lower()
                                    if destroy_all == 'yes' or yes:
                                        os.chdir('../providers/Azure')
                                        process = subprocess.Popen(f'terraform destroy -auto-approve -var="cluster_name={azure_cluster_name}" -var="location={azure_cluster_region}" -var="resource_group={azure_resource_group}" ', shell=True, stdout=subprocess.PIPE, universal_newlines=True)
                                        print("The rest of the resources are being destroyed... ")
                                        exit_code = process.wait()
                                        if exit_code == 0:
                                            print("The rest of the resources are destroyed ")
                                        else:
                                            print("The destroy of the resources failed")
                                    else:
                                        print("You choose not to destroy other resources")
                                        exit()
                                elif confirmation == 'no':
                                    print("The destruction of the cluster has been canceled.")
                                else:
                                    print("Invalid response. Please provide a valid response (yes/no).")

                            except subprocess.CalledProcessError as e:
                                print("Error occurred during 'az aks delete' command. Please check the command and try again.")
                        else:
                            print(f"The AKS cluster named {azure_cluster_name} in resource group {azure_resource_group} does not exist.")
                            return

                    except subprocess.CalledProcessError as e:
                        print("Error occurred during 'az aks show' command. Please check the command and try again.")

                elif cluster_provider == "GCP":
                    gcp_cluster_name = cluster.get('cluster_name')
                    gcp_cluster_region = cluster.get('cluster_region')
                    gcp_cluster_project = cluster.get('cluster_project')

                    # Check if the cluster exists in the cluster credentials
                    matching_cluster = next((c for c in data if c.get('cluster_name') == gcp_cluster_name and c.get('cluster_region') == gcp_cluster_region and c.get('cluster_project') == gcp_cluster_project), None)

                    if matching_cluster:
                        print(f"The GKE cluster named {gcp_cluster_name} in region {gcp_cluster_region} and project {gcp_cluster_project} exists.")
                        if yes:
                            confirmation = 'yes'
                        else:
                            confirmation = input("Are you sure that you want to destroy this cluster? (yes/no): ").lower()
                        if confirmation == 'yes':
                            # Retrieve the available zones for the specified region using the Google Cloud API
                            zone_command = f"gcloud compute zones list --filter='{gcp_cluster_region}' --format='value(name)'"
                            try:
                                zones_output = subprocess.check_output(zone_command, shell=True).decode().strip()
                                zones = zones_output.splitlines()

                                if not zones:
                                    print(f"No zones found for region {gcp_cluster_region}.")
                                    return

                                cluster_deleted = False

                                for zone in zones:
                                    describe_command = f"gcloud container clusters describe {gcp_cluster_name} --zone {zone} --format='value(zone)'"
                                    try:
                                        subprocess.check_output(describe_command, stderr=subprocess.STDOUT, shell=True)
                                    except subprocess.CalledProcessError as e:
                                        continue  # Cluster not found in this zone, move on to the next zone

                                    # Cluster found in this zone, delete it
                                    print('Deleting the cluster that has been found.')
                                    delete_command = f"gcloud container clusters delete {gcp_cluster_name} --zone {zone} --quiet"
                                    subprocess.check_output(delete_command, stderr=subprocess.STDOUT, shell=True)
                                    cluster_deleted = True

                                if cluster_deleted:
                                    print(f"The GKE cluster named {gcp_cluster_name} in region {gcp_cluster_region} has been deleted successfully.")
                                else:
                                    print(f"No GKE cluster named {gcp_cluster_name} found in any zone of region {gcp_cluster_region}.")
                                data.remove(cluster)
                                with open('cluster_credentials/clusters.yaml', 'w') as file:
                                    yaml.dump(data, file)
                                if yes:
                                    destroy_all = 'yes'
                                else:
                                    destroy_all = input("Do you want to destroy all other resources? (yes/no): ").lower()
                                if destroy_all == 'yes':
                                    os.chdir('../providers/GCP')
                                    process = subprocess.Popen(f'terraform destroy -auto-approve -var="project={gcp_cluster_project}"', shell=True, stdout=subprocess.PIPE, universal_newlines=True)
                                    print("The rest of the resources are being destroyed...")
                                    exit_code = process.wait()
                                    if exit_code == 0:
                                        print("The rest of the resources are destroyed ")
                                    else:
                                        print("The destroy of the resources failed")
                                else:
                                    print("You choose not to destroy other resources")
                                    exit()
                            except subprocess.CalledProcessError as e:
                                print("An error occurred while retrieving the available zones. Please check the command and try again.")

                        elif confirmation == 'no':
                            print("The destruction of the cluster has been canceled.")
                        else:
                            print("Invalid response. Please provide a valid response (yes/no).")

                    else:
                        print(f"The GKE cluster named {gcp_cluster_name} in region {gcp_cluster_region} does not exist.")


@cli.command()
@click.option('--type', type=click.Choice(['operator', 'deployment']), required=False, default="deployment", help='Type of how to deploy operator')
@click.argument('product', type=click.Choice(['nginx', 'istio', 'karpenter']))
@click.option('--version', type=click.STRING, help="product version", required=False)
@click.option('--yes', '-y', is_flag=True, help='Automatically answer "yes" to all prompts and proceed.')
def add(type, product, version, yes):
    """
    Adds a product in the current cluster.

    :param type: TODO
    :param product: TODO
    :param version: TODO
    :param yes: TODO
    """
    product_cat = dict()
    installed_type = dict()
    deploymentFile = dict()
    operatorRepo = dict()
    operatorDir = dict()
    operatorImage = dict()
    imageVersion = dict()  # TODO this shouldn't be here, use default version instead
    operatorVersion = dict()
    with open("catalog/catalog.yaml", 'r') as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            if line.startswith('- product'):
                product_cat['product'] = line.split(':')[1].strip()
            elif line.startswith('installed_type'):
                installed_type['installed_type'] = line.split(':')[1].strip()
            elif line.startswith('deploymentFile'):
                deploymentFile['deploymentFile'] = line.split(':')[1].strip()
            elif line.startswith('operatorDir'):
                operatorDir['operatorDir'] = line.split(':')[1].strip()
            elif line.startswith('operatorRepo'):
                operatorRepo['operatorRepo'] = line.split(': ')[1].strip()
            elif line.startswith('operatorImage'):
                operatorImage['operatorImage'] = line.split(': ')[1].strip()
            elif line.startswith('imageVersion'):
                imageVersion['imageVersion'] = line.split(': ')[1].strip()
            elif line.startswith('operatorVersion'):
                operatorVersion['operatorVersion'] = line.split(': ')[1].strip()
    if installed_type['installed_type'] == "deployment":
        type = 'operator'
        deploy = Deploy(op_version=operatorVersion['operatorVersion'], productName=product)
        if yes:
            deploy.switch_operator(productName=product, autoApprove='yes')
        else:
            deploy.switch_operator(productName=product, autoApprove='no')
    if installed_type['installed_type'] == "operator":
        type = 'deployment'
        deploy = Deploy(op_version=operatorVersion['operatorVersion'], productName=product, operatorDir=operatorDir['operatorDir'])
        if yes:
            deploy.switch_deployment(productName=product, autoApprove='yes')
        else:
            deploy.switch_deployment(productName=product, autoApprove='no')
    if type == 'operator' and product == 'nginx':
        deploy = Deploy(op_version=operatorVersion['operatorVersion'], deployment_type=deploymentFile['deploymentFile'], imageVersion=imageVersion['imageVersion'], operatorImage=operatorImage['operatorImage'], operatorRepo=operatorRepo['operatorRepo'], operatorDir=operatorDir['operatorDir'], productName=product, installed_type=type)
        deploy.operator(productName=product, operatorRepo=operatorRepo['operatorRepo'])
    if type == 'deployment' and product == 'nginx':
        deploy = Deploy(deployment_type=deploymentFile['deploymentFile'], imageVersion=imageVersion['imageVersion'], operatorDir=operatorDir['operatorDir'], operatorImage=operatorImage['operatorImage'], productName=product, installed_type=type, op_version=operatorVersion['operatorVersion'])
        deploy.deployment(productName=product, operatorRepo=operatorRepo['operatorRepo'])


@cli.command()
@click.option('--type', type=click.Choice(['operator', 'deployment']), help='Type of how to deploy operator')
@click.argument('product', type=click.Choice(['nginx', 'istio', 'karpenter']))
@click.option('--version', type=click.STRING, default='1.4.1', help="Operator version", required=False)
def update(type, product, version):
    """
    Updates a product in the current cluster.

    :param type: TODO
    :param product: TODO
    :param version: TODO
    """
    if type == 'operator':
        print(f'Upadating {product} with latest version ({version})')
        repo_dir = f'catalog/{product}/operator'
        if not os.path.exists(repo_dir):
            # FIXME get operator repo from catalog and use Deploy object
            subprocess.run(['git', 'clone', 'https://github.com/nginxinc/nginx-ingress-helm-operator/',
                            '--branch', f'v{version}'])
        os.chdir(repo_dir)
        subprocess.run(['git', 'checkout', f'v{version}'])
        # Update the Operator
        img = f'nginx/nginx-ingress-operator:{version}'
        subprocess.run(['make', 'deploy', f'IMG={img}'])
        subprocess.run(['kubectl', 'get', 'deployments', '-n', 'nginx-ingress-operator-system'])

        print(f'Nginx operator updated successfully with {version} version')
    elif type == 'deployment':
        # FIXME delete all of this and just use the catalog + new image version on Deploy
        product_cat = dict()
        installed_type = dict()
        deploymentFile = dict()
        operatorRepo = dict()
        operatorDir = dict()
        operatorImage = dict()
        imageVersion = dict()
        installed_version = dict()
        with open("catalog/catalog.yaml", 'r') as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                if line.startswith('- product'):
                    product_cat['product'] = line.split(':')[1].strip()
                elif line.startswith('installed_type'):
                    installed_type['installed_type'] = line.split(':')[1].strip()
                elif line.startswith('deploymentFile'):
                    deploymentFile['deploymentFile'] = line.split(':')[1].strip()
                elif line.startswith('operatorDir'):
                    operatorDir['operatorDir'] = line.split(':')[1].strip()
                elif line.startswith('operatorRepo'):
                    operatorRepo['operatorRepo'] = line.split(': ')[1].strip()
                elif line.startswith('operatorImage'):
                    operatorImage['operatorImage'] = line.split(': ')[1].strip()
                elif line.startswith('imageVersion'):
                    imageVersion['imageVersion'] = line.split(': ')[1].strip()
                elif line.startswith('installed_version'):
                    installed_version['installed_version'] = line.split(': ')[1].strip()
        if installed_type is None and installed_version is None:
            print("Deployment is not installed")
        print(f"Updating the deployment to version: {version}")
        deploy = Deploy(deployment_type=deploymentFile['deploymentFile'], imageVersion=version, operatorDir=operatorDir['operatorDir'], operatorImage=operatorImage['operatorImage'], productName=product, installed_type=type, op_version=version)
        deploy.deployment(productName=product, operatorRepo=operatorRepo['operatorRepo'])

        print(f"Deployment is updated to {imageVersion['imageVersion']}")

    else:
        print('Invalid configuration.')


@cli.command()
@click.option('--type', type=click.Choice(['operator', 'deployment']), help='Type of how to deploy operator')
@click.argument('product', type=click.Choice(['nginx', 'istio', 'karpenter']))
def delete(type, product):
    """
    Deletes a product in the current cluster.

    :param type: TODO
    :param product: TODO
    """
    installed_type = dict()
    operatorRepo = dict()
    operatorVersion = dict()
    operatorImage = dict()
    operatorDir = dict()
    deploymentFile = dict()
    imageVersion = dict()
    with open("catalog/catalog.yaml", 'r') as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            if line.startswith('installed_type'):
                installed_type['installed_type'] = line.split(':')[1].strip()
            elif line.startswith('operatorRepo'):
                operatorRepo['operatorRepo'] = line.split(': ')[1].strip()
            elif line.startswith('operatorVersion'):
                operatorVersion['operatorVersion'] = line.split(': ')[1].strip()
            elif line.startswith('operatorImage'):
                operatorImage['operatorImage'] = line.split(': ')[1].strip()
            elif line.startswith('operatorDir'):
                operatorDir['operatorDir'] = line.split(':')[1].strip()
            elif line.startswith('deploymentFile'):
                deploymentFile['deploymentFile'] = line.split(':')[1].strip()
            elif line.startswith('imageVersion'):
                imageVersion['imageVersion'] = line.split(': ')[1].strip()
    if type == 'operator':
        print(f'Deleting {product} with {imageVersion["imageVersion"]} version')
        os.chdir(operatorDir['operatorDir'])
        # Delete the deployed operator
        subprocess.run(['make', 'undeploy'])
        data = [
            {
                'product': f'{product}',
                'default_version': 'latest',
                'default_type': 'deployment',
                'available_types': ['deployment', 'operator'],
                'installed_version': '',
                'installed_type': '',
                'operatorRepo': operatorRepo['operatorRepo'],
                'operatorVersion': '1.5.0',
                'operatorImage': operatorImage['operatorImage'],
                'operatorDir': operatorDir['operatorDir'],
                'deploymentFile': deploymentFile['deploymentFile'],
                'imageVersion': imageVersion['imageVersion']
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
        print(f'{product} operator deleted successfully with {imageVersion["imageVersion"]} version')
    elif type == 'deployment':
        deploy_file = deploymentFile['deploymentFile']
        deploy_version = imageVersion['imageVersion']
        print(f"Deleting {product} deployment with {deploy_version} image version")
        subprocess.run(['kubectl', 'delete', '-f', f'{deploy_file}'])
        data = [
            {
                'product': f'{product}',
                'default_version': f'{imageVersion}',
                'default_type': 'deployment',
                'available_types': ['deployment', 'operator'],
                'installed_version': '',
                'installed_type': '',
                'operatorRepo': operatorRepo['operatorRepo'],
                'operatorVersion': operatorVersion['operatorVersion'],
                'operatorImage': operatorImage['operatorImage'],
                'operatorDir': operatorDir['operatorDir'],
                'deploymentFile': deploymentFile['deploymentFile'],
                'imageVersion': imageVersion['imageVersion']
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
    else:
        print('Invalid configuration.')


@cli.command()
@click.argument('type', type=click.Choice(['cluster']))
@click.argument('cluster', type=click.STRING)
@click.option('--provider', '-pr', type=click.Choice(['AWS', 'Azure', 'GCP']), default=None, help='Cloud provider of the cluster (AWS, Azure, or GCP)')
@click.option('--region', '-r', type=click.STRING, default=None, help='Region of the cluster (AWS and GCP)')
@click.option('--resource-group', '-rg', type=click.STRING, default=None, help='Resource group of the cluster (Azure)')
@click.option('--project', '-p', type=click.STRING, default=None, help='GCP project of the cluster (GCP)')
def use(type, cluster, provider, region, resource_group, project):
    """
    Select a cluster to switch to.

    :param type: TODO
    :param cluster: TODO
    :param provider: TODO
    :param region: TODO
    :param resource_group: TODO
    :param project: TODO
    """
    # FIXME it has just to read the clusters.yaml once they connect the first time it is referred by a unique name
    if type != 'cluster':
        print("Invalid argument type. Please provide 'cluster' as the argument type.")
        return

    if provider == 'AWS':
        if not region:
            print("Region is required.")
            print("Please provide the --region <cluster-region> or -r <cluster-region> option.")
            return
    elif provider == 'Azure':
        if not resource_group:
            print("Resource group is required.")
            print("Please provide the --resource-group <resource-group> or -rg <resource-group> option.")
            return
    elif provider == 'GCP':
        if not project:
            print("GCP project is required.")
            print("Please provide the --project <project-id> or -pr <project-id> option.")
            return
        if not region:
            print("Region is required.")
            print("Please provide the --region <cluster-region> or -r <cluster-region> option.")
            return

    else:
        print("Invalid provider. Please provide 'AWS', 'Azure', or 'GCP' as the provider.")
        print("Use the --provider <cloud-provider> or -pr <cloud-provider> option.")
        return

    cluster_dir = 'cluster_credentials'
    os.makedirs(cluster_dir, exist_ok=True)

    cluster_file = os.path.join(cluster_dir, 'clusters.yaml')

    if os.path.exists(cluster_file):
        with open(cluster_file, 'r') as file:
            try:
                data = yaml.safe_load(file)
                if not data:
                    data = []
            except yaml.YAMLError as e:
                print("Error loading clusters.yaml:", str(e))
                return
    else:
        data = []

    cluster_info = next((c for c in data if c.get('cluster_name') == cluster), None)

    if cluster_info is None:
        # Cluster not managed, add it to data list
        if provider == 'AWS':
            cluster_info = {
                'cluster_credentials': "credentials/aws_kube_credential",
                'cluster_name': f"{cluster}",
                'cluster_provider': provider.upper(),
                'cluster_region': f"{region}",
                'managed_by': "USER",
            }
        elif provider == 'Azure':
            cluster_info = {
                'cluster_credentials': "credentials/azure_kube_credential",
                'cluster_name': f"{cluster}",
                'cluster_provider': provider.upper(),
                'cluster_resource_group': f"{resource_group}",
                'managed_by': "USER",
            }
        elif provider == 'GCP':
            cluster_info = {
                'cluster_credentials': "credentials/gcp_kube_credential",
                'cluster_name': f"{cluster}",
                'cluster_provider': provider.upper(),
                'cluster_project': f"{project}",
                'managed_by': "USER",
            }

        data.append(cluster_info)

    elif cluster_info.get('managed_by') == 'USER':
        # Cluster already managed by USER, no modification needed
        pass

    else:
        # Cluster managed by us
        cluster_info['managed_by'] = 'KUBELAB'

    # Update the Kubernetes configuration based on the cluster's cloud provider
    if provider == 'AWS':
        update_kubeconfig_cmd = ["aws", "eks", "update-kubeconfig", "--region", region, "--name", cluster]
    elif provider == 'Azure':
        update_kubeconfig_cmd = ["az", "aks", "get-credentials", "--resource-group", resource_group, "--name", cluster, "--overwrite-existing"]
    elif provider == 'GCP':
        update_kubeconfig_cmd = ["gcloud", "container", "clusters", "get-credentials", cluster, "--project", project, "--region", region]

    update_kubeconfig_process = subprocess.run(update_kubeconfig_cmd)

    if update_kubeconfig_process.returncode != 0:
        print(f"Failed to connect to the {provider.upper()} cluster. The clusters.yaml file will not be modified.")
        return

    with open(cluster_file, 'w') as file:
        try:
            yaml.safe_dump(data, file)
        except yaml.YAMLError as e:
            print("Error saving clusters.yaml:", str(e))
            return


@cli.command()
def info():
    """
    Query your cluster for information via an interactive shell from Mondoo.
    """
    print("Information about your cluster come from cnquery lib - thanks Mondoo")
    subprocess.run(['cnquery', 'shell', 'k8s'])


if __name__ == '__main__':
    cli()
