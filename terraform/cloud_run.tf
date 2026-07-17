# Cloud Run V2 definition for the FastAPI Backend REST Gateway
resource "google_cloud_run_v2_service" "web_backend" {
  name     = "regudrift-web"
  location = var.region

  template {
    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/regudrift-repo/web:latest"

      env {
        name  = "ENV"
        value = "production"
      }
      env {
        name  = "VECTOR_STORE_PROVIDER"
        value = "qdrant"
      }
      env {
        name  = "QDRANT_URL"
        value = "http://${google_compute_instance.qdrant_vm.network_interface[0].network_ip}:6333"
      }
      env {
        name  = "DATABASE_URL"
        value = "postgresql+asyncpg://${google_sql_user.db_user.name}:${google_sql_user.db_user.password}@${google_sql_database_instance.postgres_instance.private_ip_address}/${google_sql_database.postgres_db.name}"
      }
      env {
        name = "GEMINI_API_KEY"
        value_source {
          secret_key_ref {
            secret  = "GEMINI_API_KEY"
            version = "latest"
          }
        }
      }

      ports {
        container_port = 8000
      }
      
      resources {
        limits = {
          cpu    = "1"
          memory = "1024Mi"
        }
      }
    }

    vpc_access {
      connector = google_vpc_access_connector.connector.id
      egress    = "PRIVATE_RANGES_ONLY" # Only route Cloud SQL and GCE private IP traffic through VPC
    }
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }
}

# Cloud Run V2 definition for the Next.js Frontend Web Application
resource "google_cloud_run_v2_service" "frontend_app" {
  name     = "regudrift-frontend"
  location = var.region

  template {
    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/regudrift-repo/frontend:latest"

      env {
        name  = "NEXT_PUBLIC_API_URL"
        value = google_cloud_run_v2_service.web_backend.uri
      }

      ports {
        container_port = 3000
      }
      
      resources {
        limits = {
          cpu    = "1"
          memory = "1024Mi"
        }
      }
    }
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }
}

# Cloud Run V2 definition for the Streamlit UI Command Center
resource "google_cloud_run_v2_service" "streamlit_ui" {
  name     = "regudrift-ui"
  location = var.region

  template {
    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/regudrift-repo/ui:latest"

      env {
        name  = "BACKEND_URL"
        value = google_cloud_run_v2_service.web_backend.uri
      }

      ports {
        container_port = 8501
      }
      
      resources {
        limits = {
          cpu    = "1"
          memory = "1024Mi"
        }
      }
    }

    vpc_access {
      connector = google_vpc_access_connector.connector.id
      egress    = "PRIVATE_RANGES_ONLY"
    }
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }
}

# IAM Policies enabling public unauthenticated access to the Frontends and API services
resource "google_cloud_run_v2_service_iam_member" "noauth_backend" {
  name     = google_cloud_run_v2_service.web_backend.name
  location = google_cloud_run_v2_service.web_backend.location
  role     = "roles/run.viewer"
  member   = "allUsers"
}

resource "google_cloud_run_v2_service_iam_member" "noauth_frontend" {
  name     = google_cloud_run_v2_service.frontend_app.name
  location = google_cloud_run_v2_service.frontend_app.location
  role     = "roles/run.viewer"
  member   = "allUsers"
}

resource "google_cloud_run_v2_service_iam_member" "noauth_ui" {
  name     = google_cloud_run_v2_service.streamlit_ui.name
  location = google_cloud_run_v2_service.streamlit_ui.location
  role     = "roles/run.viewer"
  member   = "allUsers"
}
