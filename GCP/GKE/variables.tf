##### Global Variables #####

variable "region" {
  description = "The region for the infrastructure."
  type        = string
  default     = "us-central1"
}

variable "project_id" {
  description = "The project ID."
  type        = string
  default     = "cts-project-388707"
}

variable "env_name" {
  description = "The environment for the infrastructure."
  type        = string
  default     = "prod"
}

##### Networking Variables #####

variable "network" {
  description = "The VPC network created to host the cluster in."
  type        = string
  default     = "gke-network"
}

variable "subnetwork" {
  description = "The subnetwork created to host the cluster in."
  type        = string
  default     = "gke-subnet"
}

variable "subnet_ip_cidr" {
  description = "IP CIDR to use for the subnet."
  type        = string
  default     = "10.10.0.0/16"
}

variable "gke_ip_range_pods_name" {
  description = "The secondary IP range name to use for pods."
  type        = string
  default     = "ip-range-pods"
}

variable "ip_cidr_range_pods" {
  description = "The secondary IP CIDR range to use for the pods."
  type        = string
  default     = "10.20.0.0/16"
}

variable "gke_ip_range_services_name" {
  description = "The secondary IP range name to use for services."
  type        = string
  default     = "ip-range-services"
}

variable "ip_cidr_range_services" {
  description = "The secondary IP range CIDR to use for services."
  type        = string
  default     = "10.30.0.0/16"
}

##### GKE Cluster Variables #####

variable "gke_zones" {
  description = "The zones to host the cluster in."
  type        = list(string)
  default     = ["us-central1-a", "us-central1-b", "us-central1-c"]
}

variable "cluster_name" {
  description = "The name for the GKE cluster"
  type        = string
  default     = "gke-terraform"
}

variable "node_pool_min_count" {
  description = "Minimum number of node pool."
  type        = number
  default     = 1
}

variable "node_pool_max_count" {
  description = "Maximum number of node pool."
  type        = number
  default     = 2
}

variable "node_pool_disksize" {
  description = "Size of the disk attached to each node, specified in GB. The smallest allowed disk size is 10GB."
  type        = number
  default     = 10
}

variable "node_pool_name" {
  description = "The name of the node pool"
  type        = string
  default     = "node-pool"
}

variable "node_pool_machine_type" {
  description = "The name of a Google Compute Engine machine type."
  type        = string
  default     = "n2-standard-2"
}

variable "gke_regional" {
  description = "Whether is a regional cluster (zonal cluster if set false. WARNING: changing this after cluster creation is destructive!)."
  type        = bool
  default     = false
}

variable "node_pool_preemptible" {
  description = "A boolean that represents whether or not the underlying node VMs are preemptible."
  type        = bool
  default     = false
}

variable "node_pool_auto_repair" {
  description = "Whether the nodes will be automatically repaired."
  type        = bool
  default     = true
}

variable "node_pool_auto_upgrade" {
  description = "Whether the nodes will be automatically upgraded."
  type        = bool
  default     = true
}

variable "gke_horizontal_pod_autoscaling" {
  description = "Enable horizontal pod autoscaling addon."
  type        = bool
  default     = true
}

variable "node_pool_autoscaling" {
  description = "	Configuration required by cluster autoscaler to adjust the size of the node pool to the current cluster usage."
  type        = bool
  default     = true
}
