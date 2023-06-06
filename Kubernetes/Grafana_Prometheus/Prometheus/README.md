### Company Name: KubeLab
#### Author: Daniel Ilievski
#### Creation Date: 2023-05-15
#### Last Updated: 2023-05-20

## About

Prometheus is an open-source monitoring toolkit for cloud-native applications and infrastructure. It collects, stores, and visualizes metrics, offering powerful insights and alerting capabilities. With Prometheus, you can monitor and proactively address performance and health issues in any scale of deployment.

## Features

- Collects metrics from configured targets at given intervals
- Provides powerful query language to analyze collected data
- Enables alerting based on defined rules

## Technical Requirements

- Kubernetes cluster version 2.5+
- Sufficient resources (CPU, memory) to run Prometheus and scrape targets
- Persistent storage for metrics data

## Design

![Prometheus Design](./Images/prometheus-architecture.png?raw=true)

Prometheus scrapes metrics from configured targets at regular intervals and stores the collected data in its time-series database. Users can query the database using the PromQL language to create graphs and visualizations, and define alerting rules to notify them of any issues.

## Deployments Target(s)

### Prometheus caters to a diverse range of users involved in the monitoring and observability of applications and infrastructure:

1. Developers: Developers can leverage Prometheus to gain insights into the performance and behavior of their applications. They can use Prometheus to monitor application-specific metrics, identify performance bottlenecks, and optimize code and resource usage.

2. DevOps Engineers: DevOps engineers rely on Prometheus for monitoring and managing the health of distributed systems and microservices architectures. They can set up monitoring pipelines, define alerting rules, and automate incident response using Prometheus' powerful features.

3. System Administrators: System administrators utilize Prometheus to monitor the health and performance of servers, network devices, and infrastructure components. They can track key metrics such as CPU usage, memory utilization, disk space, and network traffic to ensure system stability and troubleshoot issues.

4. Site Reliability Engineers (SREs): SREs rely on Prometheus to ensure the reliability and availability of applications and services. They use Prometheus' monitoring and alerting capabilities to detect anomalies, respond to incidents, and implement proactive measures to prevent service disruptions.

5. Operations Teams: Operations teams responsible for managing cloud infrastructure can benefit from Prometheus by monitoring resource utilization, tracking cost metrics, and ensuring the efficient use of cloud resources.

### The main reasons to use Prometheus:

1. Monitoring Cloud-Native Applications: Prometheus is designed specifically for monitoring modern, cloud-native applications and infrastructure. It seamlessly integrates with popular technologies such as Kubernetes, Docker, and microservices architectures.

2. Robust Metrics Collection: Prometheus excels at collecting and storing time-series data, making it easy to track and analyze key metrics related to performance, resource usage, and application health.

3. Powerful Querying Language: Prometheus offers a flexible and expressive query language called PromQL. This allows users to extract meaningful insights from their metrics data and create custom dashboards and visualizations.

4. Alerting and Alert Management: Prometheus provides a comprehensive alerting system that enables users to define and manage alerts based on metric thresholds and other conditions. It can send alerts via various channels like email, Slack, or PagerDuty.

5. Scalability and Reliability: Prometheus is built to handle large-scale deployments and can handle high volumes of metrics data. It offers a highly reliable and fault-tolerant architecture, ensuring continuous monitoring even in complex environments.

## Dependencies
- Kubernetes Cluster that is already configured and working, to be able to deploy Prometheus on it.
- If you want to have persistent data for Prometheus, you need to have AWS EFS deployed and configured with this module.

## Licensing Information
- Prometheus is licensed under the Apache License, Version 2.0.

## Parameters
| Parameter                                         | Type       | Default                                                        | Description                                 |
| ------------------------------------------------- | ---------- | -------------------------------------------------------------- | ------------------------------------------- |
| template_path                                     | String     | Prometheus-EKS/prometheus.yaml                                 | Path to Prometheus template                 |
| namespace                                         | String     | ❌ No Default Value                                            | Namespace in which Prometheus be deployed   |
| volumes                                           | Boolean    | false                                                          | Enable Persistent data for Prometheus       |
| prometheus_cluster_role_metadata_name             | String     | prometheus                                                     | Cluster Role Metadata Name                  |
| prometheus_cluster_role_file_path                 | List       | Prometheus-EKS/configuration/cluster_role.yaml                 | Path to the Cluster Roles                   |
| cluster_roles.cluster_role_binding_name           | String     | default_cluster_role_binding                                   | Cluster Role Binding Metadata Name          |
| cluster_roles.cluster_service_account_name        | String     | default                                                        | Prometheus Service Account Name             |
| prometheus_configmap_configuration_name           | String     | prometheus-server-conf                                         | Prometheus Configuariton Metadata Name      |
| prometheus_configmap_labels                       | Dictionary | name: prometheus-server-conf                                   | Labels for Prometheus ConfigMap             |
| prometheus_rules_file_path                        | String     | Prometheus-EKS/configuration/prometheus.rules                  | Path to the Prometheus rules file           |
| prometheus_configuration_file_path                | String     | Prometheus-EKS/configuration/prometheus.yml                    | Path to the main Prometheus configurations  |
| prometheus_efs_sc_metadata_name                   | String     | prometheus-efs-sc                                              | Name for the Prometheus Storage Class       |
| prometheus_efs_sc_provisioner                     | String     | efs.csi.aws.com                                                | Provisioner for the Prometheus Storage Class|
| prometheus_efs_sc_provisioningMode                | String     | efs-ap                                                         | ProvisioningMode for the Prometheus SC      |
| prometheus_efs_sc_fileSystemId                    | String     | ❌ No Default Value                                            | AWS Elastic File System Id                  |
| prometheus_efs_sc_directoryPerms                  | Number     | 755                                                            | AWS EFS Directory Permissions               |
| prometheus_efs_sc_basePath                        | String     | /prometheus_dynamic_provisioning                               | AWS EFS Base Path                           |
| prometheus_efs_pvc_metadata_name                  | String     | prometheus-efs-pvc                                             | Persistent Volume Claim Metadata Name       |
| prometheus_efs_pvc_accessModes                    | List       | ReadWriteMany                                                  | Persistent Volume Claim Access Modes        |
| prometheus_efs_pvc_resources_storage              | String     | 5Gi                                                            | Persistent Volume Claim Resources Storage   |
| prometheus_deployment_metadata_name               | String     | prometheus-deployment                                          | Prometheus Deployment Metadata Name         |
| prometheus_deployment_labels                      | Dictionary | app: prometheus-server                                         | Labels for Prometheus Deployment            |
| prometheus_deployment_spec_replicas               | Number     | 1                                                              | Number of replicas for Prometheus Deployment|
| prometheus_deployment_container_name              | String     | prometheus-container                                           | Prometheus Deployment Container Name        |
| prometheus_deployment_container_image             | String     | prom/prometheus                                                | Prometheus Deployment Container Image       |
| prometheus_storage_tsdb_path                      | String     | /prometheus/                                                   | Path for TSDB Storage Prometheus            |
| prometheus_deployment_container_port              | Number     | 9090                                                           | Prometheus Deployment Container Port        |
| prometheus_deployment_config_volume_name          | String     | prometheus-config-volume                                       | Prometheus Configuration Volume Name        |
| prometheus_deployment_config_volume_mountPath     | String     | /etc/prometheus/                                               | Prometheus Configuration Volume Mounth Path |
| prometheus_deployment_config_volume_defaultMode   | Number     | 420                                                            | Prometheus Configuration Volume Default Mode|
| prometheus_deployment_efs_volume_name             | String     | prometheus-volume                                              | Prometheus Persistent Volume Name           |
| prometheus_deployment_efs_volume_mountPath        | String     | /prometheus                                                    | Prometheus Persistent Volume Mounth Path    |
| prometheus_service_metadata_name                  | String     | prometheus-service                                             | Prometheus Service Metadata Name            |
| prometheus_service_port_name                      | String     | web-http                                                       | Prometheus Service Port Name                |
| prometheus_service_port                           | Number     | 9090                                                           | Prometheus Service Port                     |
