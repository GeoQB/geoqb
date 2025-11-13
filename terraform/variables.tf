variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

# GKE Variables
variable "node_count" {
  description = "Initial number of nodes"
  type        = number
  default     = 2
}

variable "min_node_count" {
  description = "Minimum number of nodes"
  type        = number
  default     = 1
}

variable "max_node_count" {
  description = "Maximum number of nodes"
  type        = number
  default     = 10
}

variable "machine_type" {
  description = "GKE node machine type"
  type        = string
  default     = "e2-standard-2"
}

variable "preemptible" {
  description = "Use preemptible nodes"
  type        = bool
  default     = false
}

# Database Variables
variable "db_tier" {
  description = "Cloud SQL tier"
  type        = string
  default     = "db-f1-micro"
}

variable "db_user" {
  description = "Database user"
  type        = string
  default     = "geoqb"
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

# Redis Variables
variable "redis_tier" {
  description = "Redis tier"
  type        = string
  default     = "BASIC"
}

variable "redis_memory_gb" {
  description = "Redis memory in GB"
  type        = number
  default     = 1
}
