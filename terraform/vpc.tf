resource "google_compute_network" "vpc_network" {
  name                    = "regudrift-vpc"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "subnet" {
  name          = "regudrift-subnet"
  ip_cidr_range = "10.0.1.0/24"
  region        = var.region
  network       = google_compute_network.vpc_network.id
  
  private_ip_google_access = true
}

# Allocate global IP range for Private Service Connection (Private IP Cloud SQL)
resource "google_compute_global_address" "private_ip_address" {
  name          = "regudrift-private-ip-alloc"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.vpc_network.id
}

# Create private connection to Google services (VPC Peering connection)
resource "google_service_networking_connection" "private_vpc_connection" {
  network                 = google_compute_network.vpc_network.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip_address.name]
}

# Serverless VPC Access Connector to allow Cloud Run instances private network access
resource "google_vpc_access_connector" "connector" {
  name          = "regu-vpc-conn"
  region        = var.region
  network       = google_compute_network.vpc_network.name
  ip_cidr_range = "10.8.0.0/28"
}
