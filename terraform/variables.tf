variable "project_id" {
  type        = string
  description = "The GCP Project ID where resources will be provisioned"
  default     = "regudrift-ai-prod"
}

variable "region" {
  type        = string
  description = "The target deployment region"
  default     = "asia-south1"
}

variable "zone" {
  type        = string
  description = "The availability zone for VM provisioning"
  default     = "asia-south1-a"
}

variable "db_password" {
  type        = string
  description = "Password for the Cloud SQL PostgreSQL master user"
  sensitive   = true
  default     = "ReguDriftSecurePass2026!"
}
