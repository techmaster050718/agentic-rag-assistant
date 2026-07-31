variable "instance_name" {}

resource "google_sql_database_instance" "instance" {
  name             = var.instance_name
  database_version = "POSTGRES_15"
  settings {
    tier = "db-f1-micro"
  }
}
