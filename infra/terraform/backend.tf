# infra/terraform/backend.tf

terraform {
  required_version = ">= 1.5.0"
  
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.20.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6.0"
    }
  }

  # Remote state storage in GCS
  # Create this bucket manually before running terraform init
  backend "gcs" {
    bucket = "your-terraform-state-bucket-name"
    prefix = "agentic-rag-assistant/prod"
  }
}