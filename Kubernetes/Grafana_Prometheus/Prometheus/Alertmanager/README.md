# About:

AlertManager is an open-source alerting system that works with the Prometheus Monitoring system.

## Features:

- Receives and aggregates alerts from various sources
- Sends notifications based on defined rules and configurations
- Integrates with various notification channels such as email, Slack and more (this needs to be configured according to your specific need)

## Technical requirements:

- A running Kubernetes cluster
- Access to a Prometheus server to scrape alerts from

## Design:

![Alertmanager Design](../Images/alert-manager.png?raw=true)

The Prometheus Server scrapes the information from the specified targets, then the Alertmanager takes the task to send notifications based on rules and configurations.

The Alertmanager integrates and can be set up with various notification channels such as email, Slack and more.

## Dependencies:

- Prometheus must be running and configured to scrape alerts
- The Alert Manager configuration must be defined in a separate configuration file or ConfigMap
- Prometheus should have the correct alert manager service endpoint in its config.yaml as shown below to send the alert to Alert Manager.

## Known Limitations/TODOs:

- Alert Manager does not support hierarchical alerts
- Alert Manager does not support deduplication of alerts
- Configuring Alert Manager can be complex, especially for more advanced use cases

## Licensing Information:
Alert Manager is licensed under the Apache License 2.0.

## Parameters:

## Config Map for Alert Manager Configuration

| Parameter                                         | Type       | Default                                                        | Description                                 |
| ------------------------------------------------- | ---------- | -------------------------------------------------------------- | ------------------------------------------- |
| template_path                                     | String     | Prometheus-EKS/Alertmanager/alert-manager.yaml                 | Path to Alert Manager template              |
| namespace                                         | String     | ❌ No Default Value                                            | Namespace in which Prometheus be deployed   |
| volumes                                           | Boolean    | false                                                          | Do you want persistent data?                |
| am_configmap_metadata_name                        | String     | alertmanager-config                                            | Alert Manager ConfigMap Metadata Name       |
| am_conf_file_path                                 | String     | Prometheus-EKS/Alertmanager/configuration/config.yml           | Alert Manager Configuration File Path       |
| am_efs_sc_metadata_name                           | String     | am-efs-sc                                                      | Alert Manager Storage Class Metadata Name   |
| am_efs_sc_provisioner                             | String     | efs.csi.aws.com                                                | Alert Manager Storage Class Provisioner     |
| am_efs_sc_provisioningMode                        | String     | efs-ap                                                         | Alert Manager Storage Class provisioningMode| 
| am_efs_sc_provisioningMode                        | String     | efs-ap                                                         | Alert Manager Storage Class provisioningMode| 
| am_efs_sc_fileSystemId                            | String     | ❌ No Default Value                                            | AWS EFS Id                             |         
| am_efs_sc_directoryPerms                          | Number     | 755                                                            | Alert Manager Storage Class directoryPerms  |
| am_efs_sc_basePath                                | String     | '/alert_manager_dynamic_provisioning'                          | Alert Manager Storage Class basePath        |
| am_efs_pvc_metadata_name                          | String     | am-efs-pvc                                                     | Alert Manager PVC Metadata Name             |
| am_efs_pvc_metadata_name                          | String     | am-efs-pvc                                                     | Alert Manager PVC Metadata Name             | 
| am_efs_pvc_accessModes                            | List       | ReadWriteMany                                                  | Alert Manager PVC accessModes               |
| am_efs_pvc_resources_storage                      | String     | 5Gi                                                            | Alert Manager PVC Resources Storage         |
| am_deployment_metadata_name                       | String     | am-deployment                                                  | Alert Manager Deployment Metadata Name      |
| am_deployment_replicas                            | Number     | 1                                                              | Alert Manager Deployment Replicas           |
| am_labels                                         | Dictionary | app: alertmanager                                              | Alert Manager Labels                        |
| am_template_metadata_name                         | String     | am-template                                                    | Alert Manager Template Metadata Name        |
| am_container_name                                 | String     | am-container                                                   | Alert Manager Container Name                |
| am_deployment_image                               | String     | prom/alertmanager:latest                                       | Alert Manager Image                         |
| am_persistent_data_storage_path                   | string     | /alertmanager                                                  | Alert Manager Persistent Data Storage Path  |
| am_deployment_container_port                      | Number     | 9093                                                           | Alert Manager Container Port                |
| am_cpu_requests                                   | String     | 500m                                                           | Alert Manager Resources Requests CPU        |
| am_memory_requests                                | String     | 500M                                                           | Alert Manager Resources Requests Memory     |
| am_cpu_limits                                     | Number     | 1                                                              | Alert Manager Resources Limits CPU          |
| am_memory_limits                                  | String     | 1Gi                                                            | Alert Manager Resources Limits Memory       |
| am_config_volume                                  | String     | config-volume                                                  | Alert Manager Config Volume Name            |
| am_config_volume_mountPath                        | String     | /etc/alertmanager                                              | Alert Manager Config Volume mountPath       |
| am_persistent_data_volume                         | String     | am-persistent-volume                                           | Alert Manager Persistent Data Volume Name   |
| am_persistent_data_storage_path                   | String     | /alertmanager                                                  | Alert Manager Persistent Data Volume mountPath |
| am_service_metadata_name                          | String     | alertmanager                                                   | Alert Manager Service Metadata Name         |
| am_prometheus_scrape                              | Dictionary | prometheus.io/scrape: 'true'                                   | Alert Manager Service Scrape Annotation     |
| am_prometheus_port                                | Dictionary | prometheus.io/port:   '9093'                                   | Alert Manager Service Port Annotation       |
| am_service_port                                   | Number     | 9093                                                           | Alert Manager Service Port                  |
| am_service_type                                   | String     | ClusterIP                                                      | Alert Manager Service Type                  |
| email_reciever_name                               | String     | alert-emailer                                                  | Email Reciever Name                         |
| email_reciever                                    | String     | ❌ No Default Value                                            | Who should get the email?                   |
| email_sender                                      | String     | ❌ No Default Value                                            | Who sends the email?                        |
| email_sender_smarthost                            | String     | ❌ No Default Value                                            | Email Sender Smart Host                     |
| email_sender_username                             | String     | ❌ No Default Value                                            | Email Sender Username                       |
| email_sender_identitiy                            | String     | ❌ No Default Value                                            | Email Sender Identity                       |
| email_sender_password                             | String     | ❌ No Default Value                                            | Email Sender Password                       |
| email_sender_require_tls                          | Boolean    | true                                                           | Email Sender Requires TLS?                  |















