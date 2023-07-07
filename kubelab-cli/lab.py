#!/usr/bin/env python3

import click
import os
import subprocess
import json
import time
import yaml
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

        # Retrieve the cluster name from the Terraform output
        try:
            completed_process = subprocess.run(['terraform', 'output', '-json'], capture_output=True, text=True, check=True)
            output_json = completed_process.stdout.strip()
            output_dict = yaml.safe_load(output_json)
            cluster_name = output_dict['cluster_name']['value']
            cluster_region = output_dict['cluster_region']['value']
        except (subprocess.CalledProcessError, KeyError) as e:
            print(f"Error: Failed to retrieve cluster name. {e}")
            return

        os.chdir('../kubelab-cli')

        # Create cluster_credentials directory if it doesn't exist
        credentials_dir = 'cluster_credentials'
        if not os.path.exists(credentials_dir):
            os.makedirs(credentials_dir)

        # Retrieve AWS credentials file path
        aws_credentials_file = os.path.join('credentials', 'aws_kube_credential')

        # Create the dictionary with cluster information
        cluster_info = {
            'cluster_name': cluster_name,
            'cluster_provider': cloud_provider,
            'cluster_region': cluster_region,
            'cluster_credentials': aws_credentials_file
        }

        # Check if the cluster name already exists in cluster.yaml
        yaml_file_path = os.path.join(credentials_dir, 'cluster.yaml')
        existing_clusters = []
        if os.path.exists(yaml_file_path):
            with open(yaml_file_path, 'r') as yaml_file:
                existing_clusters = yaml.safe_load(yaml_file)
                existing_clusters = existing_clusters if existing_clusters is not None else []

        cluster_names = [cluster['cluster_name'] for cluster in existing_clusters]

        if cluster_name in cluster_names:
            print(f"The cluster name {cluster_name} already exists in cluster.yaml. Skipping append.")
        else:
            existing_clusters.append(cluster_info)
            # Save updated cluster information to YAML file
            with open(yaml_file_path, 'w') as yaml_file:
                yaml.dump(existing_clusters, yaml_file)

            # Print the deployed cluster name
            print(f"{cluster_name} has been deployed.")

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


@cli.command()
@click.argument('type', type=click.Choice(['cluster']))
def list(type):
    if type == 'cluster':
        credentials_dir = 'cluster_credentials'
        yaml_file_path = os.path.join(credentials_dir, 'cluster.yaml')

        if not os.path.exists(yaml_file_path):
            click.echo("No cluster.yaml file found.")
            return

        with open(yaml_file_path, 'r') as yaml_file:
            clusters = yaml.safe_load(yaml_file)

        if not clusters:
            click.echo("No clusters found.")
            return

        click.echo("Clusters:")
        for cluster in clusters:
            click.echo(f"- cluster_name: {cluster['cluster_name']}")
            click.echo(f"  cluster_provider: {cluster['cluster_provider']}")
            click.echo(f"  cluster_region: {cluster['cluster_region']}")
            click.echo(f"  cluster_credentials: {cluster['cluster_credentials']}")
            click.echo()
    else:
        print("You have selected a wrong type, run 'lab list --help' for more information.")


@cli.command()
@click.argument('param_type', type=click.Choice(['cluster']))
@click.option('--name', type=click.STRING, help='What is the cluster named as? (AWS, Azure, GCP)')
@click.option('--region', type=click.STRING, help='Where is the cluster located? (AWS)')
@click.option('--resource_group', type=click.STRING, help='What is the resource group of the cluster? (Azure)')
@click.option('--zone', type=click.STRING, help='Where is the cluster located? (GCP)')
def destroy(param_type, name, region, resource_group, zone):
    with open('state/lab_state.json', 'r') as file:
        data = json.load(file)
        initialized_cloud_provider = data.get('initialized_cloud_provider')
    if param_type == 'cluster' and initialized_cloud_provider == "AWS":
        # If you don't specify name and region
        if name is None and region is None:
            os.chdir('../AWS')
            subprocess.run(['terraform', 'plan', '-destroy', '-target=module.EKS'])

            print("You have not selected a specific cluster name and cluster region.")
            confirmation = input("Are you sure you want to destroy the currently used AWS cluster? (yes/no): ").lower()
            if confirmation == 'yes':
                try:
                    subprocess.check_call(['terraform', 'destroy', '-target=module.EKS', '-auto-approve'])
                    print("The cluster has been destroyed.")
                except subprocess.CalledProcessError:
                    print("Error occurred during Terraform destroy. Please check the command and try again.")
                    return
            elif confirmation == 'no':
                print("The destruction of the cluster has been canceled.")
            else:
                print("Invalid response. Please provide a valid response (yes/no).")
        # If you specify name and region
        elif name is not None and region is not None:
            print(f"You have selected to destroy cluster: {name} that is located in: {region}")
            check_command = f"aws eks describe-cluster --name {name} --region {region}"
            try:
                subprocess.check_output(check_command, stderr=subprocess.STDOUT, shell=True)
            except subprocess.CalledProcessError as e:
                if "ResourceNotFoundException" in e.output.decode():
                    print(f"The EKS cluster named {name} in region {region} does not exist.")
                else:
                    print("Error occurred during describe-cluster command. Please check the command and try again.")
                return

            confirmation = input("Are you sure that you want to destroy this cluster? (yes/no): ").lower()
            if confirmation == 'yes':
                check_command = f"aws eks list-nodegroups --cluster-name {name} --region {region}"

                try:
                    check_output = subprocess.check_output(check_command, stderr=subprocess.STDOUT, shell=True)
                except subprocess.CalledProcessError:
                    print("Error occurred during list-nodegroups command. Please check the command and try again.")
                    return

                if check_output:
                    node_groups = json.loads(check_output)['nodegroups']
                    
                    for node_group in node_groups:
                        check_command = f"aws eks list-nodegroups --cluster-name {name} --region {region}"

                        delete_node_group_command = f"aws eks delete-nodegroup --cluster-name {name} --nodegroup-name {node_group} --region {region}"
                        print(f"Node group {node_group} is being destroyed..")
                        subprocess.Popen(delete_node_group_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True).communicate() 

                        while True:
                            # Run the AWS CLI command to list node groups
                            check_command = f"aws eks list-nodegroups --cluster-name {name} --region {region}"
                            result = subprocess.run(check_command, shell=True, capture_output=True, text=True)

                            if result.returncode == 0:
                                # Parse the JSON output
                                output = json.loads(result.stdout)

                                if "nodegroups" in output and len(output["nodegroups"]) == 0:
                                    print(f"The Node Groups of the {name} cluster have been destroyed.")
                                    break

                            else:
                                print("An error occurred while executing the command.")
                delete_command = f"aws eks delete-cluster --name {name} --region {region}"
                print(f"The EKS cluster {name} in region {region} is being destroyed..")
                subprocess.check_call(delete_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)

                while True:
                    check_cluster_command = f"aws eks describe-cluster --name {name} --region {region}"
                    try:
                        check_output = subprocess.check_output(check_cluster_command, stderr=subprocess.STDOUT, shell=True)
                    except subprocess.CalledProcessError as e:
                        if "ResourceNotFoundException" in e.output.decode():
                            print(f"The EKS cluster named {name} in region {region} has been destroyed.")
                            break
                        else:
                            print("Error occurred during describe-cluster command. Please check the command and try again.")
                            return

            elif confirmation == 'no':
                print("The destruction of the cluster has been canceled.")
            else:
                print("Invalid response. Please provide a valid response (yes/no).")

            # Remove the cluster from cluster.yaml file
            credentials_dir = 'cluster_credentials'
            yaml_file_path = os.path.join(credentials_dir, 'cluster.yaml')

            if not os.path.exists(yaml_file_path):
                click.echo("No cluster.yaml file found.")
                return

            with open(yaml_file_path, 'r') as yaml_file:
                clusters = yaml.safe_load(yaml_file)

            if not clusters:
                click.echo("No clusters found.")
                return

            filtered_clusters = [c for c in clusters if c['cluster_name'] != name]

            if len(filtered_clusters) == len(clusters):
                click.echo(f"Cluster '{name}' not found in cluster.yaml.")
                return

            with open(yaml_file_path, 'w') as yaml_file:
                yaml.dump(filtered_clusters, yaml_file)

            click.echo(f"Cluster '{name}' in region '{region}' has been destroyed and removed from cluster.yaml.")
        else:
            print(f"The entry for the destroy command is invalid, run: bash lab destroy --help")
    elif param_type == 'cluster' and initialized_cloud_provider == "Azure":
        if name is None and resource_group is None:
            os.chdir('../Azure')
            subprocess.run(['terraform', 'plan', '-destroy', '-target=module.AKS'])

            print("You have not selected a specific cluster name and cluster resource group.")
            confirmation = input("Are you sure you want to destroy the currently used Azure cluster? (yes/no): ").lower()
            if confirmation == 'yes':
                try:
                    subprocess.check_call(['terraform', 'destroy', '-target=module.AKS', '-auto-approve'])
                    print("The cluster has been destroyed.")
                except subprocess.CalledProcessError:
                    print("Error occurred during Terraform destroy. Please check the command and try again.")
                    return
            elif confirmation == 'no':
                print("The destruction of the cluster has been canceled.")
            else:
                print("Invalid response. Please provide a valid response (yes/no).")
        # If you specify name and resource_group
        elif name is not None and resource_group is not None:
            try:
                describe_command = f"az aks show --name {name} --resource-group {resource_group} --query provisioningState --output tsv"
                result = subprocess.check_output(describe_command, stderr=subprocess.STDOUT, shell=True)
                provisioning_state = result.decode().strip()

                if provisioning_state == "Succeeded":
                    print(f"The AKS cluster named {name} in resource group {resource_group} exists.")
                    try:
                        confirmation = input("Are you sure that you want to destroy this cluster? (yes/no): ").lower()
                        if confirmation == 'yes':
                            delete_command = f"az aks delete --name {name} --resource-group {resource_group} --yes"
                            subprocess.check_output(delete_command, stderr=subprocess.STDOUT, shell=True)
                            print(f"The AKS cluster named {name} in resource group {resource_group} has been deleted successfully.")
                        elif confirmation == 'no':
                            print("The destruction of the cluster has been canceled.")
                        else:
                            print("Invalid response. Please provide a valid response (yes/no).")

                    except subprocess.CalledProcessError as e:
                        print("Error occurred during 'az aks delete' command. Please check the command and try again.")
                else:
                    print(f"The AKS cluster named {name} in resource group {resource_group} does not exist.")
                    return

            except subprocess.CalledProcessError as e:
                print("Error occurred during 'az aks show' command. Please check the command and try again.")

        else:
            print(f"The entry for the destroy command is invalid, run: bash lab destroy --help")
    # Destroy cluster that is currently in use with the GCP provider
    elif param_type == 'cluster' and initialized_cloud_provider == "GCP":
        if name is None and zone is None:
            os.chdir('../GCP')
            subprocess.run(['terraform', 'plan', '-destroy', '-target=module.GKE'])

            print("You have not selected a specific cluster name and cluster resource group.")
            confirmation = input("Are you sure you want to destroy the currently used GKE cluster? (yes/no): ").lower()
            if confirmation == 'yes':
                try:
                    subprocess.check_call(['terraform', 'destroy', '-target=module.GKE', '-auto-approve'])
                    print("The cluster has been destroyed.")
                except subprocess.CalledProcessError:
                    print("Error occurred during Terraform destroy. Please check the command and try again.")
                    return
            elif confirmation == 'no':
                print("The destruction of the cluster has been canceled.")
            else:
                print("Invalid response. Please provide a valid response (yes/no).")
        # If you specify name and resource_group
        if name is not None and zone is not None:
            try:
                describe_command = f"gcloud container clusters describe {name} --zone {zone} --format='value(status)'"
                result = subprocess.check_output(describe_command, stderr=subprocess.STDOUT, shell=True)
                provisioning_state = result.decode().strip()

                if provisioning_state == "RUNNING":
                    print(f"The GKE cluster named {name} in zone {zone} exists.")
                    try:
                        confirmation = input("Are you sure that you want to destroy this cluster? (yes/no): ").lower()
                        if confirmation == 'yes':
                            delete_command = f"gcloud container clusters delete {name} --zone {zone} --quiet"
                            subprocess.check_output(delete_command, stderr=subprocess.STDOUT, shell=True)
                            print(f"The GKE cluster named {name} in zone {zone} has been deleted successfully.")
                        elif confirmation == 'no':
                            print("The destruction of the cluster has been canceled.")
                        else:
                            print("Invalid response. Please provide a valid response (yes/no).")

                    except subprocess.CalledProcessError as e:
                        print("Error occurred during 'gcloud container clusters delete' command. Please check the command and try again.")
                else:
                    print(f"The GKE cluster named {name} in zone {zone} does not exist.")
                    return

            except subprocess.CalledProcessError as e:
                print("Error occured during 'lab destroy' command.")
                print(f"The specified {name} cluster located in {zone} was not found.")
                print("For more information please run 'lab destroy --help'.")

    else:
        print(f"The entry for the destroy command is invalid, run: bash lab destroy --help")


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
@click.argument('name', type=click.Choice(['cluster', 'role', 'rbac']))
@click.argument('cluster', type=click.STRING)
@click.option('--region', type=click.STRING, help='Region of the cluster')
@click.option('--resource-group', type=click.STRING, help='Resource group of the cluster')
def use(name, cluster, region, resource_group):
    with open('state/lab_state.json', 'r') as file:
        data = json.load(file)
        initialized_cloud_provider = data.get('initialized_cloud_provider')

    if initialized_cloud_provider == "AWS":
        if region is None:
            print("Region is required for AWS, use --region YOUR-CLUSTER-REGION while running the command.")
            return
        subprocess.run(["aws", "eks", "update-kubeconfig", "--region", region, "--name", cluster])
    elif initialized_cloud_provider == "Azure":
        if resource_group is None:
            print("Resource group is required for Azure, use --resource-group YOUR-RESOURCE-GROUP while running the command.")
            return
        subprocess.run(["az", "aks", "get-credentials", "--resource-group", resource_group, "--name", cluster, "--overwrite-existing"])
    elif initialized_cloud_provider == "GCP":
        if region is None:
            print("Region is required for GCP, use --region YOUR-CLUSTER-REGION while running the command.")
            return
        subprocess.run(["gcloud", "container", "clusters", "get-credentials", cluster, "--region=" + region])
    else:
        print("Unsupported cloud provider.")
        return


@cli.command()
def info():
    return "Hello"


if __name__ == '__main__':
    cli()
