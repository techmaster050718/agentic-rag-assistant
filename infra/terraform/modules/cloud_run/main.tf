# infra/terraform/modules/cloud_run/main.tf

variable "project_id" { type = string }
variable "region" { type = string }
variable "environment" { type = string }
variable "openai_api_key" { type = string }
variable "langchain_api_key" { type = string }
variable "db_connection_name" { type = string }
variable "db_user" { type = string }
variable "db_password" { type = string }
variable "db_name" { type = string }
variable "gcs_bucket_name" { type = string }

# --- Service Account for Backend ---
resource "google_service_account" "backend" {
  account_id   = "rag-backend-${var.environment}"
  display_name = "RAG Backend Service Account"
  project      = var.project_id
}

# Grant Backend SA access to Cloud SQL
resource "google_project_iam_member" "backend_sql_client" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.backend.email}"
}

# Grant Backend SA access to GCS
resource "google_project_iam_member" "backend_storage_admin" {
  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.backend.email}"
}

# --- Backend Cloud Run Service ---
resource "google_cloud_run_v2_service" "backend" {
  name     = "rag-backend-${var.environment}"
  location = var.region
  project  = var.project_id

  template {
    service_account = google_service_account.backend.email

    containers {
      # This image will be pushed by GitHub Actions
      image = "us-docker.pkg.dev/${var.project_id}/rag-repo/backend:latest"

      ports {
        container_port = 8000
      }

      env {
        name  = "APP_ENV"
        value = "production"
      }
      env {
        name  = "OPENAI_API_KEY"
        value = var.openai_api_key
      }
      env {
        name  = "LANGCHAIN_TRACING_V2"
        value = "true"
      }
      env {
        name  = "LANGCHAIN_API_KEY"
        value = var.langchain_api_key
      }
      env {
        name  = "POSTGRES_USER"
        value = var.db_user
      }
      env {
        name  = "POSTGRES_PASSWORD"
        value = var.db_password
      }
      env {
        name  = "POSTGRES_DB"
        value = var.db_name
      }
      # Cloud SQL Proxy exposes the DB on localhost
      env {
        name  = "POSTGRES_HOST"
        value = "127.0.0.1"
      }
      env {
        name  = "POSTGRES_PORT"
        value = "5432"
      }
      env {
        name  = "GCS_BUCKET_NAME"
        value = var.gcs_bucket_name
      }
      env {
        name  = "BACKEND_CORS_ORIGINS"
        value = "[\"*\"]" # Restrict to frontend URL in strict prod
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
      }
    }

    # Connect to Cloud SQL instance
    volumes {
      name = "cloudsql"
      cloud_sql_instance {
        instances = [var.db_connection_name]
      }
    }

    scaling {
      min_instance_count = 0
      max_instance_count = 5
    }

    timeout = "300s" # 5 minutes for long-running ingestion tasks
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }
}

# Allow public access to Backend API
resource "google_cloud_run_v2_service_iam_member" "backend_public" {
  location = google_cloud_run_v2_service.backend.location
  name     = google_cloud_run_v2_service.backend.name
  project  = var.project_id
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# --- Frontend Cloud Run Service ---
resource "google_cloud_run_v2_service" "frontend" {
  name     = "rag-frontend-${var.environment}"
  location = var.region
  project  = var.project_id

  template {
    containers {
      image = "us-docker.pkg.dev/${var.project_id}/rag-repo/frontend:latest"

      ports {
        container_port = 3000
      }

      env {
        name  = "NEXT_PUBLIC_API_URL"
        value = google_cloud_run_v2_service.backend.uri
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "256Mi"
        }
      }
    }

    scaling {
      min_instance_count = 0
      max_instance_count = 5
    }
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }
}

# Allow public access to Frontend
resource "google_cloud_run_v2_service_iam_member" "frontend_public" {
  location = google_cloud_run_v2_service.frontend.location
  name     = google_cloud_run_v2_service.frontend.name
  project  = var.project_id
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# --- Outputs ---
output "backend_url" {
  value = google_cloud_run_v2_service.backend.uri
}

output "frontend_url" {
  value = google_cloud_run_v2_service.frontend.uri
}