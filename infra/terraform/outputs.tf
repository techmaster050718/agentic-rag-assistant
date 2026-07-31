# infra/terraform/outputs.tf

output "frontend_url" {
  description = "The public URL of the Frontend Cloud Run service"
  value       = module.cloud_run.frontend_url
}

output "backend_url" {
  description = "The public URL of the Backend Cloud Run service"
  value       = module.cloud_run.backend_url
}

output "database_connection_name" {
  description = "The connection name for the Cloud SQL instance"
  value       = module.cloud_sql.connection_name
}