#!/usr/bin/env python3

import click
import os
import subprocess
import json
from catalog.nginx.deploy import Deploy
import shutil
import fnmatch


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

        # Retrieve the cluster name from the Terraform output
        try:
            completed_process = subprocess.run(['terraform', 'output', '-json'], capture_output=True, text=True, check=True)
            output_json = completed_process.stdout.strip()
            output_dict = yaml.safe_load(output_json)
            cluster_name = output_dict['cluster_name']['value']
            cluster_region = output_dict['cluster_region']['value']
            cluster_resource_group = output_dict['cluster_resource_group']['value']
        except (subprocess.CalledProcessError, KeyError) as e:
            print(f"Error: Failed to retrieve cluster name. {e}")
            return

        os.chdir('../kubelab-cli')

        # Create cluster_credentials directory if it doesn't exist
        credentials_dir = 'cluster_credentials'
        if not os.path.exists(credentials_dir):
            os.makedirs(credentials_dir)

        # Retrieve Azure credentials file path
        azure_credentials_file = os.path.join('credentials', 'azure_kube_credential')

        # Create the dictionary with cluster information
        cluster_info = {
            'cluster_name': cluster_name,
            'cluster_provider': cloud_provider,
            'cluster_credentials': azure_credentials_file,
            'cluster_region': cluster_region,
            'cluster_resource_group': cluster_resource_group
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
    elif name == 'cluster' and cloud_provider == "GCP":
        print(f"Creating cluster in {cloud_provider}")
        os.chdir('../GCP')
        subprocess.run(['terraform', 'apply', '-auto-approve'])

        # Retrieve the cluster name from the Terraform output
        try:
            completed_process = subprocess.run(['terraform', 'output', '-json'], capture_output=True, text=True, check=True)
            output_json = completed_process.stdout.strip()
            output_dict = yaml.safe_load(output_json)
            cluster_name = output_dict['cluster_name']['value']
            cluster_region = output_dict['cluster_region']['value']
            cluster_project = output_dict['cluster_project']['value']
        except (subprocess.CalledProcessError, KeyError) as e:
            print(f"Error: Failed to retrieve cluster name. {e}")
            return

        os.chdir('../kubelab-cli')

        # Create cluster_credentials directory if it doesn't exist
        credentials_dir = 'cluster_credentials'
        if not os.path.exists(credentials_dir):
            os.makedirs(credentials_dir)

        # Retrieve GCP credentials file path
        gcp_credentials_file = os.path.join('credentials', 'gcp_kube_credential')

        # Create the dictionary with cluster information
        cluster_info = {
            'cluster_name': cluster_name,
            'cluster_provider': cloud_provider,
            'cluster_credentials': gcp_credentials_file,
            'cluster_region': cluster_region,
            'cluster_project': cluster_project
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
    elif name == 'rbac':
        click.echo("This feature will be available soon")


@cli.command()
@click.argument('type', type=click.Choice(['cluster']))
@click.option('--provider', type=click.Choice(['AWS', 'Azure', 'GCP']), help='Filter clusters by provider')
@click.option('--name', help='Filter clusters by name pattern')
def list(type, provider, name):
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
def destroy(param_type, name, region):
    if param_type == "cluster":
        if name is None and region is None:
            print("Please provide both the cluster name and region.")
        elif name is None:
            print("Please provide the cluster name.")
        elif region is None:
            print("Please provide the cluster region.")
        else:
            # Load cluster credentials from YAML file
            with open('cluster_credentials/cluster.yaml', 'r') as file:
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

                    elif confirmation == 'no':
                        print("The destruction of the cluster has been canceled.")
                    else:
                        print("Invalid response. Please provide a valid response (yes/no).")

                elif cluster_provider == "Azure":
                    azure_cluster_name = cluster.get('cluster_name')
                    azure_resource_group = cluster.get('cluster_resource_group')

                    try:
                        describe_command = f"az aks show --name {azure_cluster_name} --resource-group {azure_resource_group} --query provisioningState --output tsv"
                        result = subprocess.check_output(describe_command, stderr=subprocess.STDOUT, shell=True)
                        provisioning_state = result.decode().strip()

                        if provisioning_state == "Succeeded":
                            print(f"The AKS cluster named {azure_cluster_name} in resource group {azure_resource_group} exists.")
                            try:
                                confirmation = input("Are you sure that you want to destroy this cluster? (yes/no): ").lower()
                                if confirmation == 'yes':
                                    delete_command = f"az aks delete --name {azure_cluster_name} --resource-group {azure_resource_group} --yes"
                                    print(f"Deleting AKS cluster named {azure_cluster_name} in resource group {azure_resource_group}.")
                                    subprocess.check_output(delete_command, stderr=subprocess.STDOUT, shell=True)
                                    print(f"The AKS cluster named {azure_cluster_name} in resource group {azure_resource_group} has been deleted successfully.")
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

                    # Check if the cluster exists in the cluster credentials
                    matching_cluster = next((c for c in data if c.get('cluster_name') == gcp_cluster_name and c.get('cluster_region') == gcp_cluster_region), None)

                    if matching_cluster:
                        print(f"The GKE cluster named {gcp_cluster_name} in region {gcp_cluster_region} exists.")

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
                                    delete_command = f"gcloud container clusters delete {gcp_cluster_name} --zone {zone} --quiet"
                                    subprocess.check_output(delete_command, stderr=subprocess.STDOUT, shell=True)
                                    cluster_deleted = True

                                if cluster_deleted:
                                    print(f"The GKE cluster named {gcp_cluster_name} in region {gcp_cluster_region} has been deleted successfully.")
                                else:
                                    print(f"No GKE cluster named {gcp_cluster_name} found in any zone of region {gcp_cluster_region}.")

                            except subprocess.CalledProcessError as e:
                                print("An error occurred while retrieving the available zones. Please check the command and try again.")

                        elif confirmation == 'no':
                            print("The destruction of the cluster has been canceled.")
                        else:
                            print("Invalid response. Please provide a valid response (yes/no).")

                    else:
                        print(f"The GKE cluster named {gcp_cluster_name} in region {gcp_cluster_region} does not exist.")

                # Remove the destroyed cluster from the cluster.yaml file
                data.remove(cluster)
                with open('cluster_credentials/cluster.yaml', 'w') as file:
                    yaml.dump(data, file)


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
    # FIXME switch between deployment/operator must be done in the specific file
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
                print("Successfully deleted nginx deployment \n")
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
                print(f"Successfully deleted nginx operator {version} version\n")
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
