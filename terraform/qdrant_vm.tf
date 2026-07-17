resource "google_compute_disk" "qdrant_ssd" {
  name  = "qdrant-storage-disk"
  type  = "pd-ssd"
  zone  = var.zone
  size  = 30 # 30GB production-ready vector collection persistent space
}

resource "google_compute_instance" "qdrant_vm" {
  name         = "regudrift-qdrant-vm"
  machine_type = "e2-medium" # 2 vCPU, 4GB RAM optimal for Qdrant index execution
  zone         = var.zone

  boot_disk {
    initialize_params {
      image = "cos-cloud/cos-stable" # Google's hardened Container-Optimized OS (has docker pre-configured)
    }
  }

  attached_disk {
    source      = google_compute_disk.qdrant_ssd.id
    device_name = "qdrant-data"
  }

  network_interface {
    subnetwork = google_compute_subnetwork.subnet.id
    # No public IP block (no access_config block) makes this VM accessible strictly via VPC/Serverless connector
  }

  # Startup script executing disk formatting, persistent mounting, and starting Qdrant container
  metadata_startup_script = <<-EOT
    #!/bin/bash
    # Format the attached SSD if it has no filesystem
    DISK_DEV="/dev/disk/by-id/google-qdrant-data"
    if ! blkid "$DISK_DEV"; then
      mkfs.ext4 -F "$DISK_DEV"
    fi
    
    # Mount persistent storage directory
    mkdir -p /mnt/disks/qdrant
    mount -o discard,defaults "$DISK_DEV" /mnt/disks/qdrant
    chmod a+w /mnt/disks/qdrant

    # Start Qdrant engine container bound to host port 6333 with volume persistence mapping
    docker run -d \
      --name qdrant-engine \
      --restart unless-stopped \
      -p 6333:6333 \
      -p 6334:6334 \
      -v /mnt/disks/qdrant:/qdrant/storage \
      qdrant/qdrant:latest
  EOT

  service_account {
    scopes = ["cloud-platform"]
  }
}

# Firewall rule allowing internal private subnet communication across Qdrant ports (6333/6334)
resource "google_compute_firewall" "allow_qdrant_internal" {
  name    = "allow-qdrant-internal"
  network = google_compute_network.vpc_network.id

  allow {
    protocol = "tcp"
    ports    = ["6333", "6334"]
  }

  source_ranges = ["10.0.1.0/24", "10.8.0.0/28"]
}
