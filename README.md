# kubelab-cli - Kubernetes utility CLI by KubeLab

kubelab-cli is a command line tool that empowers developers to effortlessly create, manage, and destroy Kubernetes clusters on popular cloud providers such as AWS, Azure, and GCP, obtaining Terraform code and easy yaml configs in return.

Additionally, it enables users to easily manage products on top of the clusters, such as NGINX, and deploy them using your own configuration as deployments, operators, CRDs...

## Features

- **Cluster Management:** Easily create, update, and destroy Kubernetes clusters on AWS, Azure, or GCP with a simple command.

- **Product Management:** Seamlessly manage products like NGINX on top of your Kubernetes clusters using different deployment strategies, including deployment, operator, Helm, and Kustomize.

- **Deployment Flexibility:** kubelab-cli provides multiple options for your deployment to cater to different use cases and preferences.

- **Automated Setup:** The tool automates the setup process for all the cloud-specific tools you need to manage Kubernetes clusters, saving you time and effort.

- **Easy Configuration:** Intuitive YAML configuration that allow you to customize the clusters and products according to your specific needs.

- **Clear Documentation:** Comprehensive documentation to guide you through the installation, setup, and usage of the kubelab-cli tool (coming soon).

## Prerequisites

Before using kubelab-cli, ensure you have the following dependencies installed on your system:

- Kubernetes CLI (kubectl)
- AWS CLI (if using AWS as a cloud provider)
- Azure CLI (if using Azure as a cloud provider)
- Google Cloud CLI (if using GCP as a cloud provider)
- Terraform CLI

Or you can use the kubelab-cli install script to install all the dependencies for you.
Run the following command to install the dependencies and the cli itself:

```bash
curl -s https://raw.githubusercontent.com/kubelab-middleware/install.sh | bash
```

## Prerequisites (contribution only)

Linter+formatter: black + flake8
https://py-vscode.readthedocs.io/en/latest/files/linting.html

Add into your .vscode/settings.json

```json
"python.linting.flake8Args": [
  "--max-line-length=180",
  "--ignore=E501,E402,F841,F401,E302,E305",
],
```

## Other means of installation

1. Download the kubelab-cli binary for your operating system from the official GitHub repository, then place the repo in a directory you like, use it via python execution or add it to your PATH.

2. Install it via pip:

```bash
pip install kubelab-cli
```

## Usage

```bash
lab [command] [options]
```

### Cluster Management

- To create a Kubernetes cluster:
  ```bash
  lab create cluster --provider [aws|azure|gcp] --name [cluster_name]
  ```

- To update a Kubernetes cluster (e.g., change node count, update version, etc.):
  ```bash
  lab update cluster --name [cluster_name] --[option1]=[value1] --[option2]=[value2] ...
  ```

- To destroy a Kubernetes cluster:
  ```bash
  lab destroy cluster --name [cluster_name]
  ```

### Product Management

- To deploy a product (e.g., NGINX) using default settings:
  ```bash
  lab use cluster [cluster_name] # a bit like kubectl use-context
  lab add [product_name] --cluster [cluster_name] --type [deployment|operator]
  ```
  or
  ```bash
  lab add [product_name] --cluster [cluster_name] --type [deployment|operator]
  ```

- To deploy a product with custom configurations:
  ```bash
  lab add [product_name] --cluster [cluster_name] --method [deployment|operator|] --config [path_to_config_file]
  ```

- To update a deployed product:
  ```bash
  lab update [product_name] --version [new version] --cluster [cluster_name] (--method [deployment|operator]) --config [path_to_updated_config_file]
  ```

- To remove a deployed product from the cluster:
  ```bash
  lab remove [product_name] --cluster [cluster_name]
  ```

## Configuration

kubelab-cli uses configuration files to define cluster and product settings. By default, it looks for config files in the `catalog/` and `clusters/` directory.

### Example Configuration (cluster_sample.yaml)

```yaml
# Clusters configuration
name: sample
provider: aws
region: us-east-1
credential_file: ~/.aws/credentials
products:
  - nginx:
      type: operator
      version: 1.0.0
      replicas: 2
      port: 80
```

### Example Configuration (catalog.yaml)

```yaml
- product: nginx
  default_version: latest
  default_type: deployment
  available_types:
    - deployment
    - operator
  installed_version: 
  installed_type: 
  operatorRepo: https://github.com/nginxinc/nginx-ingress-helm-operator/
  operatorVersion: 1.5.0
  operatorImage: nginx/nginx-ingress-operator
  operatorDir: catalog/nginx/nginx-ingress-helm-operator
  deploymentFile: catalog/nginx/deployment/deployment.yaml
  imageVersion: latest
- product: istio
  default_version: latest
  default_type: deployment
  available_types:
    - deployment
    - operator
  installed_version:
  installed_type:
  operatorRepo: https://github.com/istio/istio/tree/master/operator
  operatorVersion: 1.20.0
  operatorImage: istio/operator
  operatorDir: catalog/istio/istio-operator
  deploymentFile: catalog/istio/deployment/deployment.yaml
  imageVersion: latest
```

## Support and Contribution

If you encounter any issues or have suggestions for improvement, please check the GitHub repository for known issues or open a new one. Contributions are highly encouraged and welcome!

## License

kubelab-cli is open-source software licensed under the [MIT License](LICENSE). Feel free to use, modify, and distribute it according to the terms of the license.

---

Thank you for using kubelab-cli! If you have any questions or need further assistance, please refer to the documentation or reach out to the [Discord community of KubeLab](https://discord.gg/aVEhdDDark) for support.

## Other OSS tools embedded or used in kubelab-cli
- https://github.com/mondoohq/cnquery
- https://github.com/derailed/k9s

## Documentation

The kubelab-cli documentation can be found [here](https://kubelab.cloud/doc).

## Security

The security policy may be [found here](SECURITY.md).