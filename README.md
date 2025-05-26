# Klab-cli - Kubernetes utility CLI

[![build](https://github.com/mbianchidev/klab-cli/actions/workflows/klab-cli.yml/badge.svg)](https://github.com/mbianchidev/klab-cli/actions/workflows/klab-cli.yml)

[![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/mbianchidev/klab-cli)](https://scorecard.dev/viewer/?uri=github.com/mbianchidev/klab-cli)

[![OpenSSF Best Practices](https://www.bestpractices.dev/projects/10609/badge)](https://www.bestpractices.dev/projects/10609)


![Homer Simpson taking an escalator to Paradise but actually falling into Platform Engineering hell](/docs/images/platform-engineering.gif)

Klab-cli is a command line tool, built in python, that empowers developers to effortlessly create, manage, and destroy Kubernetes clusters on popular cloud providers such as AWS, Azure, and GCP, obtaining Terraform code and easy yaml configs in return.

Additionally, it enables users to easily manage products on top of the clusters, such as NGINX, and deploy them using your own configuration as deployments, operators, CRDs...

## Features

- **Cluster Management:** Easily create, update, and destroy Kubernetes clusters on AWS, Azure, or GCP with a simple command.

- **Product Management:** Seamlessly manage products like NGINX on top of your Kubernetes clusters using different deployment strategies, including deployment, operator, Helm, and Kustomize.

- **Deployment Flexibility:** klab-cli provides multiple options for your deployment to cater to different use cases and preferences.

- **Automated Setup:** The tool automates the setup process for all the cloud-specific tools you need to manage Kubernetes clusters, saving you time and effort.

- **Easy Configuration:** Intuitive YAML configuration that allow you to customize the clusters and products according to your specific needs.

- **Clear Documentation:** Comprehensive documentation to guide you through the installation, setup, and usage of the klab-cli tool (coming soon).

## Prerequisites

Before using klab-cli, ensure you have the following dependencies installed on your system:

- Python 3.11.x
- Kubernetes CLI (kubectl)
- AWS CLI (if using AWS as a cloud provider)
- Azure CLI (if using Azure as a cloud provider)
- Google Cloud CLI (if using GCP as a cloud provider)
- Terraform CLI

Or you can use the klab-cli install script to install all the dependencies for you.
Run the following command to install the dependencies and the cli itself:

```bash
curl -s https://raw.githubusercontent.com/mbianchidev/klab-cli/main/install.sh | bash
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

A. Download the klab-cli binary for your operating system from the official GitHub repository, then place the repo in a directory you like, use it via python execution or add it to your PATH.

B. Install it via pip:

```bash
pip install klab-cli
```

## Usage

```bash
lab [command] [options]
```

### Cluster Management

- To create a Kubernetes cluster:
  ```bash
  lab create cluster --provider [AWS|Azure|GCP] --name [cluster_name]
  ```

- To destroy a Kubernetes cluster:
  ```bash
  lab destroy cluster --name [cluster_name]
  ```

### Cloud Native Products

- To deploy a product (e.g., NGINX) using default settings:
  ```bash
  lab add [product_name] --cluster [cluster_name] --type [deployment|operator]
  ```

- To update a deployed product:
  ```bash
  lab update [product_name] --version [new version] --cluster [cluster_name] (--type [deployment|operator])
  ```

- To remove a deployed product from the cluster:
  ```bash
  lab remove [product_name] --cluster [cluster_name]
  ```

## Configuration

klab-cli uses configuration files to define cluster and product settings. By default, it looks for config files in the `catalog/` and `clusters/` directory.
As for the `providers/` folder it is used to store the terraform code for each cloud provider.
We have set up a structure for you to follow on IaC code, but you can customize and extend it to your liking, be aware that the code requires variables in order to be as generic as possible.

### Example Configuration (cluster_sample.yaml)

```yaml
# Clusters configuration
name: sample
provider: aws
region: us-east-1
credential_file: ~/.aws/credentials
products:
  - name: nginx
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

klab-cli is open-source software licensed under the [MIT License](LICENSE). Feel free to use, modify, and distribute it according to the terms of the license.

---

Thank you for using klab-cli! If you have any questions or need further assistance, please refer to the documentation or reach out to [maintainers](docs/CONTRIBUTING.md##Maintainers) for support.

## Other OSS tools embedded or used in klab-cli
- https://github.com/mondoohq/cnquery
- https://github.com/derailed/k9s

## Documentation

Documentation can be found [here](https://mb-consulting.dev/doc). (coming soon)

## Security

The security policy may be [found here](SECURITY.md).
