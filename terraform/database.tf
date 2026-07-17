resource "google_sql_database_instance" "postgres_instance" {
  name             = "regudrift-db-instance"
  database_version = "POSTGRES_15"
  region           = var.region

  depends_on = [google_service_networking_connection.private_vpc_connection]

  settings {
    tier = "db-f1-micro"
    
    ip_configuration {
      ipv4_enabled    = false # Disable public IP access completely for secure operations
      private_network = google_compute_network.vpc_network.id
    }

    backup_configuration {
      enabled    = true
      start_time = "02:00"
    }
  }

  deletion_protection = false # Set to false to allow clean terraform teardowns during staging/evaluation
}

resource "google_sql_database" "postgres_db" {
  name     = "regudrift"
  instance = google_sql_database_instance.postgres_instance.name
}

resource "google_sql_user" "db_user" {
  name     = "reguuser"
  instance = google_sql_database_instance.postgres_instance.name
  password = var.db_password
}
