### Company Name: KubeLab
#### Author: Daniel Ilievski
#### Creation Date: 2023-05-18
#### Last Updated: 2023-05-20
# About:
This module provides the Kube State Metrics, which is a service that listens to the Kubernetes API server and generates metrics about the state of Kubernetes objects like Deployments, Nodes, and Pods.

## Features:

- Provides metrics about the state of Kubernetes objects
- Metrics include details about Deployments, Nodes, and Pods
- Metrics can be used to monitor the health and performance of Kubernetes clusters

## Technical Requirements:

- Kubernetes cluster
- Access to the Kubernetes API server
- Appropriate permissions to deploy Kube State Metrics

## Design:
![Kube State Metrics Design](../Images/kube-state-metrics.png?raw=true)

The Kube State Metrics service is designed to run as a Kubernetes deployment with a single replica. 

The deployment consists of a container that runs the Kube State Metrics server.

## Deployments Target(s):
This module targets developers and system administrators who want to monitor the health and performance of Kubernetes clusters. 

Kube State Metrics can be used to generate metrics that can be used to troubleshoot issues and optimize the performance of Kubernetes clusters.

## Dependencies:

- Kubernetes Cluster
- Running Prometheus Server
- Access to the Kubernetes API server to generate metrics about K8s objects.

## Known Limitations/TODOs:
One known limitation of Kube State Metrics is that it does not generate metrics for custom resources or third-party objects. 

However, it can be extended to support custom resources by adding custom metrics exporters.

## Licensing Information:
Kube State Metrics is licensed under the Apache License, Version 2.0.

## Parameters
| Parameter                                         | Type       | Default                                                        | Description                                  |
| ------------------------------------------------- | ---------- | -------------------------------------------------------------- | -------------------------------------------- |
| template_path                                     | String     | Prometheus-EKS/Kube-State-Metrics/kube-state-metrics.yaml      | Path to Kube State Metrics templat           |
| namespace                                         | String     | kube-system                                                    | Where the Kube State Metrics objects operate |
| ksm_labels                                        | Dictionary | app.kubernetes.io/component: exporter, app.kubernetes.io/name: kube-state-metrics, app.kubernetes.io/version: kube-state-metrics | Labels for KSM |
| ksm_cluster_role_file_path                        | List       | Prometheus-EKS/Kube-State-Metrics/configuration/ksm_cluster_role.yaml | KSM Cluster Role Files Path |
| cluster_role.ksm_cluster_role_binding_metadata_name | String     | kube-state-metrics-crb                               | Kube State Metrics Cluster Role Binding Metadata Name |
| cluster_role.ksm_cluster_role_metadata_name       | String     | kube-state-metrics-cr                                          | KSM Cluster Role Metadata Name |
| cluster_role.ksm_service_account_metadata_name    | String     | kube-state-metrics-sa                                          | Kube State Metrics Service Account Name Metadata|
| ksm_deployment_metadata_name                      | String     | kube-state-metrics-d                                           | Kube State Metrics Deployment Metadata Name |
| ksm_deployment_replicas                           | Number     | 1                                                              | Number of replicas of the deployment        |
| ksm_deployment_container_image                    | String     | registry.k8s.io/kube-state-metrics/kube-state-metrics:v2.8.2   | Image for the Kube State Metrics Deployment |
| ksm_livenessProbe_path                            | String     | /healthz                                                       | Path for the livnessProbe                   |
| ksm_livenessProbe_port                            | Number     | 8080                                                           | Port for the livnessProbe                   |
| ksm_livenessProbe_initialDelaySeconds             | Number     | 5                                           | Number of seconds to wait before starting the health checks    |
| ksm_livenessProbe_timeoutSeconds                  | Number     | 5                | Maximum number of seconds a health check probe can take before it is considered a failure |
| ksm_deployment_container_name                     | String     | kube-state-metrics-deployment                                  | Name for the Kube State Metrics container   |
| ksm_containerPort                                 | Number     | 8080                                                           | Port that the Kube State Metrics container use|
| ksm_containerPort_name                            | String     | http-metrics                                                   | Name for the Port that the KMS Container use |
| ksm_telemetry_containerPort                       | Number     | 8081                                                           | Port for Telemetry                          |
| ksm_telemetry_containerPort_name                  | String     | telemetry                                                      | Name for the Telemetry port                 |
| ksm_readinessProbe_path                           | String     | /                                                              | Path for the Readiness Probe                 |
| ksm_readinessProbe_port                           | Number     | 8081                                                           | Port for the Readiness Probe                 |
| ksm_readinessProbe_initialDelaySeconds            | Number     | 5 | Number of seconds to wait after the container starts before initiating the first readiness probe |
| ksm_readinessProbe_timeoutSeconds                 | Number     | 5 | Maximum amount of time in seconds that the readiness probe should wait for a response |
| ksm_deployment_nodeSelector                       | String     | kubernetes.io/os: linux | Node selector that determines which nodes the Pods should be scheduled onto |
| ksm_service_metadata_name                         | String     | kube-state-metrics                                              | Metadata Name of the Service |