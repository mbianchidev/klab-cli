# Labctl - Kubernetes utility CLI by KubeLab

Labctl is a command line tool that empowers developers to effortlessly create, manage, and destroy Kubernetes clusters on popular cloud providers such as AWS, Azure, and GCP, obtaining Terraform code and easy yaml configs in return.

Additionally, it enables users to easily manage products on top of the clusters, such as NGINX, and deploy them using various methods like deployment, operator or custom (like Helm, and Kustomize - coming soon).

## Features

- **Cluster Management:** Easily create, update, and destroy Kubernetes clusters on AWS, Azure, or GCP with a simple command.

- **Product Management:** Seamlessly manage products like NGINX on top of your Kubernetes clusters using different deployment strategies, including deployment, operator, Helm, and Kustomize.

- **Deployment Flexibility:** Labctl provides multiple options for your deployment to cater to different use cases and preferences.

- **Automated Setup:** The tool automates the setup process for all the cloud-specific tools you need to manage Kubernetes clusters, saving you time and effort.

- **Easy Configuration:** Intuitive YAML configuration that allow you to customize the clusters and products according to your specific needs.

- **Clear Documentation:** Comprehensive documentation to guide you through the installation, setup, and usage of the labctl tool (coming soon).

## Prerequisites

Before using labctl, ensure you have the following dependencies installed on your system:

- Kubernetes CLI (kubectl)
- AWS CLI (if using AWS as a cloud provider)
- Azure CLI (if using Azure as a cloud provider)
- Google Cloud CLI (if using GCP as a cloud provider)

Or you can use the labctl install script to install all the dependencies for you.
Run the following command to install the dependencies:

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

## Installation

1. Download the labctl binary for your operating system from the official GitHub repository.

2. Place the binary in a directory accessible from your system's PATH variable.

3. Ensure the binary has executable permissions. If not, you can set them using `chmod +x labctl`.

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
  labctl update cluster --name [cluster_name] --[option1]=[value1] --[option2]=[value2] ...
  ```

- To destroy a Kubernetes cluster:
  ```bash
  labctl destroy cluster --name [cluster_name]
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
  labctl remove [product_name] --cluster [cluster_name]
  ```

## Configuration

Labctl supports configuration files to define cluster and product settings. By default, it looks for a configuration file in the `credentials/` directory named `clusters.yaml`. You can also specify a custom configuration file using the `--config` flag.

### Example Configuration (clusters.yaml)

```yaml
# Clusters configuration
cluster:
  name: my-cluster
  provider: aws
  region: us-west-2
```

### Example Configuration (catalog.yaml)

```yaml
# Product configuration
products:
  - name: nginx
    method: deployment
    version: 3.0.2
    values_file: nginx-values.yaml
```


## Support and Contribution

If you encounter any issues or have suggestions for improvement, please check the GitHub repository for known issues or open a new one. Contributions are highly encouraged and welcome!

## License

Labctl is open-source software licensed under the [MIT License](LICENSE). Feel free to use, modify, and distribute it according to the terms of the license.

---

Thank you for using labctl! If you have any questions or need further assistance, please refer to the documentation or reach out to the [Discord community of KubeLab](https://discord.gg/aVEhdDDark) for support.

## Other OSS tools embedded or used in labctl
https://github.com/mondoohq/cnquery
https://github.com/derailed/k9s

# The Solidity Contract-Oriented Programming Language

[![Matrix Chat](https://img.shields.io/badge/Matrix%20-chat-brightgreen?style=plastic&logo=matrix)](https://matrix.to/#/#ethereum_solidity:gitter.im)
[![Gitter Chat](https://img.shields.io/badge/Gitter%20-chat-brightgreen?style=plastic&logo=gitter)](https://gitter.im/ethereum/solidity)
[![Solidity Forum](https://img.shields.io/badge/Solidity_Forum%20-discuss-brightgreen?style=plastic&logo=discourse)](https://forum.soliditylang.org/)
[![Twitter Follow](https://img.shields.io/twitter/follow/solidity_lang?style=plastic&logo=twitter)](https://twitter.com/solidity_lang)
[![Mastodon Follow](https://img.shields.io/mastodon/follow/000335908?domain=https%3A%2F%2Ffosstodon.org%2F&logo=mastodon&style=plastic)](https://fosstodon.org/@solidity)

You can talk to us on Gitter and Matrix, tweet at us on Twitter or create a new topic in the Solidity forum. Questions, feedback, and suggestions are welcome!

Solidity is a statically typed, contract-oriented, high-level language for implementing smart contracts on the Ethereum platform.

For a good overview and starting point, please check out the official [Solidity Language Portal](https://soliditylang.org).

## Table of Contents

- [Background](#background)
- [Build and Install](#build-and-install)
- [Example](#example)
- [Documentation](#documentation)
- [Development](#development)
- [Maintainers](#maintainers)
- [License](#license)
- [Security](#security)

## Background

Solidity is a statically-typed curly-braces programming language designed for developing smart contracts
that run on the Ethereum Virtual Machine. Smart contracts are programs that are executed inside a peer-to-peer
network where nobody has special authority over the execution, and thus they allow anyone to implement tokens of value,
ownership, voting, and other kinds of logic.

When deploying contracts, you should use the latest released version of
Solidity. This is because breaking changes, as well as new features and bug fixes, are
introduced regularly. We currently use a 0.x version
number [to indicate this fast pace of change](https://semver.org/#spec-item-4).

## Build and Install

Instructions about how to build and install the Solidity compiler can be
found in the [Solidity documentation](https://docs.soliditylang.org/en/latest/installing-solidity.html#building-from-source).


## Example

A "Hello World" program in Solidity is of even less use than in other languages, but still:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity >=0.6.0 <0.9.0;

contract HelloWorld {
    function helloWorld() external pure returns (string memory) {
        return "Hello, World!";
    }
}
```

To get started with Solidity, you can use [Remix](https://remix.ethereum.org/), which is a
browser-based IDE. Here are some example contracts:

1. [Voting](https://docs.soliditylang.org/en/latest/solidity-by-example.html#voting)
2. [Blind Auction](https://docs.soliditylang.org/en/latest/solidity-by-example.html#blind-auction)
3. [Safe remote purchase](https://docs.soliditylang.org/en/latest/solidity-by-example.html#safe-remote-purchase)
4. [Micropayment Channel](https://docs.soliditylang.org/en/latest/solidity-by-example.html#micropayment-channel)

## Documentation

The kubelab-cli documentation can be found [here](https://kubelab.cloud/doc).

## Development

kubelab-cli is under development. Contributions are always welcome!
Please follow the
[Developers Guide](https://kubelab.cloud/dev)
if you want to help.

You can find our current feature and bug priorities for forthcoming
releases in the [projects section](https://github.com/orgs/KubeLab-cloud/projects/2).

## License
kubelab-cli is licensed under [MIT License](LICENSE.txt).

## Security

The security policy may be [found here](SECURITY.md).