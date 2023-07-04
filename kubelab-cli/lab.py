#!/usr/bin/env python3

import click
import os
import subprocess
import json
import time


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
            os.makedirs(os.path.dirname(credential_file_path), exist_ok=True)
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
            print("Initalizing terraform..")
            os.chdir('../AWS')
            subprocess.run(['terraform', 'init'])
        else:
            click.echo('AWS credentials file not found. Please enter the credentials.')
            profile = click.prompt('AWS Profile')
            aws_access_key_id = click.prompt('AWS Access Key ID')
            aws_secret_access_key = click.prompt('AWS Secret Access Key', hide_input=True)

            # Save the credentials to a file
            credential_file_path = 'credentials/aws_kube_credential'
            os.makedirs(os.path.dirname(credential_file_path), exist_ok=True)
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
            print("Initalizing terraform..")
            os.chdir('../AWS')
            subprocess.run(['terraform', 'init'])
    elif cp == 'Azure':
        try:
            # Use Azure CLI to retrieve the currently logged-in Azure account
            result = subprocess.run(['az', 'account', 'show'], capture_output=True, text=True)
            if result.returncode == 0:
                output = result.stdout.strip()

                # Save the credentials to a file
                credential_file_path = 'credentials/azure_kube_credential.json'
                os.makedirs(os.path.dirname(credential_file_path), exist_ok=True)

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
                print("Initalizing terraform..")
                os.chdir('../Azure')
                subprocess.run(['terraform', 'init'])
            else:
                click.echo('Azure login failed. Please make sure Azure CLI is installed and logged in.')
        except Exception as e:
            click.echo(f'Error occurred while retrieving Azure credentials: {str(e)}')
    elif cp == 'GCP':
        try:
            # Retrieve the GCP application default credentials file path
            gcp_credentials_file = os.path.expanduser('~/.config/gcloud/application_default_credentials.json')
            if os.path.isfile(gcp_credentials_file):
                # Set the destination file path
                credential_file_path = 'credentials/gcp_kube_credential.json'
                os.makedirs(os.path.dirname(credential_file_path), exist_ok=True)
                # Copy the GCP application default credentials file
                with open(gcp_credentials_file, 'r') as src_file, open(credential_file_path, 'w') as dest_file:
                    dest_file.write(src_file.read())

                click.echo(f'Credentials saved to {credential_file_path}')

                # Save the state
                state = {'initialized_cloud_provider': 'GCP'}
                state_file_path = 'state/lab_state.json'
                os.makedirs(os.path.dirname(state_file_path), exist_ok=True)  # Create 'state' folder if it doesn't exist
                with open(state_file_path, 'w') as f:
                    json.dump(state, f)
                click.echo(f'State saved to {state_file_path}')
                print("Initializing Terraform...")
                os.chdir('../GCP')
                subprocess.run(['terraform', 'init'])
            else:
                click.echo('GCP application default credentials file not found. Please make sure you have authenticated with gcloud and have application default credentials.')
        except Exception as e:
            click.echo(f'Error occurred while retrieving GCP credentials: {str(e)}')
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
    elif name == 'cluster' and initialized_cloud_provider == "GCP":
        print(f"Creating cluster in {initialized_cloud_provider} ")
        os.chdir('../GCP')
        network_result = subprocess.run(['terraform', 'apply', '-target=module.gcp-network', '-auto-approve'])
        if network_result.returncode == 0:
            print("Networking deployment successful.")
        else:
            print("Something went wrong, Networking have not been deployed.")
        gke_cluster_result = subprocess.run(['terraform', 'apply', '-target=module.GKE', '-auto-approve'])
        if gke_cluster_result.returncode == 0:
            print("Kubernetes cluster deployment successful.")
        else:
            print("Something went wrong, Kubernetes cluster have not been deployed.")
            
    elif name == 'rbac':
        click.echo("This feature will be available soon")


@cli.command()
@click.argument('param_type', type=click.Choice(['cluster']))
@click.option('--name', type=click.STRING, help='What is the cluster named as?')
@click.option('--region', type=click.STRING, help='Where is the cluster located?')
@click.option('--resource_group', type=click.STRING, help='What is the resource group of the cluster?')
def destroy(param_type, name, region, resource_group):
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
        # Destroy cluster that is currently in use with the Azure provider
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
        os.chdir('../GCP')
        subprocess.run(['terraform', 'plan', '-destroy', '-target=module.GKE'])
        confirmation = input("Are you sure you want to destroy the cluster? (yes/no): ").lower()

        if confirmation == 'yes':
            subprocess.run(['terraform', 'destroy', '-target=module.GKE', '-auto-approve'])
            print("The cluster has been destroyed.")
        elif confirmation == 'no':
            print("The destruction of the cluster has been canceled.")
        else:
            print("Invalid response. Please provide a valid response (yes/no).")
    else:
        print("Please provide a valid cloud provider (AWS, Azure or GCP)")


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
