### Company Name: KubeLab
#### Author: Daniel Ilievski
#### Creation Date: 2023-05-15
#### Last Updated: 2023-05-17

## About

Grafana is a powerful data visualization and monitoring tool. It allows you to easily create and explore interactive dashboards, providing insights into your data from multiple datasources.

## Design

![Grafana Design](./Images/grafana-design.png?raw=true)

- In this example, Prometheus is responsible for collecting and storing metrics, while Grafana is responsible for visualizing and alerting on those metrics.

- Grafana is not limited to only use Prometheus as a datasource, it can be configured to work with multiple different datasources at a time.

## Deployments Target(s)

### Grafana is a versatile tool that can be beneficial to a wide range of users:

1. DevOps and System Administrators: Grafana provides real-time monitoring and visualization capabilities, allowing DevOps and system administrators to gain insights into the performance and health of their infrastructure. It enables them to track metrics, set up alerts, and troubleshoot issues efficiently.

2. Data Analysts and Data Scientists: Grafana enables data analysts and data scientists to explore and visualize data from multiple sources, making it easier to uncover patterns, trends, and correlations. With its interactive dashboards and powerful querying capabilities, Grafana facilitates data exploration and analysis.

2. Business Stakeholders and Managers: Grafana's intuitive dashboards and visualizations make it an excellent tool for business stakeholders and managers to monitor key performance indicators (KPIs) and track business metrics. It provides a comprehensive overview of the business's performance and facilitates data-driven decision-making.

3. Developers: Grafana offers various APIs and integration options, allowing developers to customize and extend its functionality. It can be integrated with existing systems and workflows, enabling developers to build customized dashboards, embed Grafana in other applications, and automate monitoring and reporting processes.

### The main reasons to use Grafana:
1. Data Visualization: Grafana excels at creating visually appealing and interactive dashboards, making it easier to understand complex data sets and identify trends or anomalies.

2. Multi-DataSource Support: Grafana supports multiple datasources, allowing users to consolidate data from various sources (e.g., databases, cloud services, APIs) into a single dashboard. This capability enables comprehensive monitoring and analysis across different systems and applications.

3. Alerting and Notifications: Grafana offers robust alerting mechanisms, allowing users to define thresholds and receive notifications when specific conditions are met. This helps in proactively addressing issues and minimizing downtime.

4. Extensibility: Grafana's open-source nature and wide range of plugins and integrations make it highly customizable and adaptable to specific needs. It can be extended to integrate with existing tools, data sources, or custom applications.

5. Community and Ecosystem: Grafana has a vibrant and active community, which means access to a wealth of resources, plugins, and community-developed dashboards. Users can leverage this ecosystem to enhance their monitoring and visualization capabilities.

## Dependencies
- Kubernetes Cluster that is already configured and working, to be able to deploy Grafana on it.

## Licensing Information
- Grafana has an open-source license under the Apache License 2.0.

## Parameters
| Parameter                                         | Type       | Default                                                        | Description                               |
| ------------------------------------------------- | ---------- | -------------------------------------------------------------- | ----------------------------------------- |
| template_path                                     | String     | Grafana/grafana.yaml                                           | Path to Grafana template                  |
| namespace                                         | String     | ❌ No Default Value                                            | Namespace in which Grafana be deployed    |
| enable_predefined_dashboards                      | Boolean    | false                                                          | Enable predefined dashboards              |
| volumes                                           | Boolean    | false                                                          | Enable Persistent data for Grafana        |
| grafana_datasources_configmap_metadata_name       | String     | grafana-datasources                                            | Datasources ConfigMap Metadat Name        |
| grafana_datasources                               | List       | Grafana/datasources/prometheus.yaml                            | Datasources for the Grafana               |
| grafana_dashboard_provider_metadata_name          | String     | grafana-provider                                               | Dashboard Providers ConfigMapadata        |
| grafana_dashboard_providers                       | List       | Grafana/dashboards/providers/k8s-prometheus.yaml               | Dashboard Providers for the Grafana       |
| grafana_dashboard_definition_metadata_name        | String     | grafana-definition                                             | Dashboard Definitions ConfigMap Metadata  |
| grafana_dashboard_definitions|List|Grafana/dashboards/definitions/kubelab-k8s-prometheus.json, Grafana/dashboards/definitions/kubelab-pods-monitor.json|Dashboard Definitions for the Grafana|
| grafana_efs_sc_metadata_name                      | String     | grafana-efs-sc                                                 | Storage Class Metadata Name               |
| grafana_efs_sc_fileSystemId                       | String     | ❌ No Default Value                                            | AWS EFS File System Id                    |
| grafana_efs_sc_provisioner                        | String     | efs.csi.aws.com                                                | Storage Class Provisioner                 |
| grafana_efs_sc_provisioningMode                   | String     | efs-ap                                                         | Storage Class provisioningMode            |
| grafana_efs_sc_directoryPerms                     | Number     | 755                                                            | AWS EFS File System Directory Permissions |
| grafana_efs_sc_basePath                           | String     | /grafana_dynamic_provisioning                                  | AWS EFS File System Directory Base Path   |
| grafana_efs_pvc_metadata_name                     | String     | grafana-efs-pvc                                                | Persistent Volume Claim Metadata Name     |
| grafana_efs_pvc_accessModes                       | List       | ReadWriteMany                                                  | Persistent Volume Claim Access Modes      |
| grafana_efs_pvc_resources_storage                 | String     | 5Gi                                                            | Persistent Volume Claim Resources Storage |
| grafana_deployment_metadata_name                  | String     | grafana-deployment                                             | Deployment Metadata Name                  |
| grafana_deployment_spec_replicas                  | Number     | 1                                                              | Deployment Replicas for Grafana           |
| grafana_deployment_labels                         | Dictionary | app: grafana                                                   | Deployment Labels for Grafana             |
| grafana_deployment_container_name                 | String     | grafana-container-name                                         | Deployment Container Name for Grafana     |
| grafana_deployment_container_image                | String     | grafana/grafana:latest                                         | Deployment Container Image for Grafana    |
| grafana_deployment_container_port_name            | String     | grafana-port                                                   | Deployment Container Name for the Port    |
| grafana_deployment_container_port                 | Number     | 3000                                                           | Deployment Container Port for Grafana     |
| grafana_deployment_efs_volume_mountPath           | String     | /var/lib/grafana                                               | Path for the Persistent Data Volume       |
| grafana_deployment_efs_volume_name                | String     | grafana-efs-vol                                                | Name for the Persistent Data Volume       |
| grafana_deployment_datasource_mountPath           | String     | /etc/grafana/provisioning/datasources                          | Path for the Datasources                  |
| grafana_datasources_configmap_volume_name         | String     | grafana-datasources-volume                                     | Name for the Datasources ConfigMap        |
| grafana_deployment_datasource_readOnly            | Boolean    | false                                                          | Are the Datasources read only?            |
| grafana_deployment_dashboard_provider_mountPath   | String     | /etc/grafana/provisioning/dashboards                           | Path for the Dashboard Provider volume    |
| grafana_dashboard_provider_volume_name            | String     | grafana-provider-volume                                        | Name for the Dashboard Provider volume    |
| grafana_deployment_dashboard_provider_readOnly    | Boolean    | false                                                          | Are the Dashboard Providers read only?    |
| grafana_deployment_dashboard_definition_mountPath | String     | /var/lib/grafana/dashboards                                    | Path for the Dashboard definitions        |
| grafana_dashboard_definition_volume_name          | String     | grafana-definition-volume                                      | Name for the Dashboard definition         |
| grafana_deployment_dashboard_definition_readOnly  | Boolean    | false                                                          | Are the Dashboard definitions read only?  |
| grafana_datasources_configmap_defaultMode         | Number     | 420                                                            | Datasources ConfigMap defaultMode         |
| grafana_dashboard_provider_defaultMode            | Number     | 420                                                            | Dashboard Providers ConfigMap defaultMode |
| grafana_service_metadata_name                     | String     | grafana-service                                                | Grafana Service Metadata Name             |
| grafana_service_scrape_annotations                | List       |"prometheus.io/scrape": "'true'", "prometheus.io/port": "'3000'"| Annotations for the Grafana Service       |
| grafana_service_expose_port                       | Number     | 80                                                             | On what port should Grafana be exposed?   |