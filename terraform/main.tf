terraform {
  required_version = ">= 1.0"
  backend "gcs" {
    bucket = "terraform-state-v8q0qvfi"
    prefix = "terraform/state/exchange-rates-ingestion"
  }

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Upload zip file to the source code bucket
resource "null_resource" "build_time" {
  triggers = {
    always_run = timestamp()
  }
}

locals {
  build_time_clean = replace(null_resource.build_time.triggers.always_run, "/[-:TZ]/", "")
}

data "google_storage_bucket" "source_code" {
  name = "source-code-cloud-functions-cyd2y7j6"
}

resource "google_storage_bucket_object" "zip_file" {
  name   = "${var.cloud_function_name}/source-code-${local.build_time_clean}.zip"
  bucket = data.google_storage_bucket.source_code.name
  source = var.zip_file_path
}

# Getting access to SA
data "google_service_account" "default" {
  account_id = var.service_account_name
}

# Creation of the Cloud Function
resource "google_pubsub_topic" "default" {
  name = "cloud-function-${var.cloud_function_name}"
}

resource "google_cloud_scheduler_job" "default" {
  name        = "cloud-function-${var.cloud_function_name}"
  description = "Scheduler to trigger the cloud function: ${var.cloud_function_name}"
  schedule    = "5 0 * * *"

  pubsub_target {
    topic_name = google_pubsub_topic.default.id
    data       = base64encode("Trigger Cloud Function")
  }
}

resource "google_cloudfunctions2_function" "default" {
  name     = var.cloud_function_name
  location = var.region

  build_config {
    runtime     = "python312"
    entry_point = var.function_entry_point
    source {
      storage_source {
        bucket = data.google_storage_bucket.source_code.name
        object = google_storage_bucket_object.zip_file.name
      }
    }
  }

  service_config {
    available_memory      = "512M"
    timeout_seconds       = 539
    max_instance_count    = 1
    service_account_email = data.google_service_account.default.email
    ingress_settings      = "ALLOW_INTERNAL_ONLY"
  }

  event_trigger {
    trigger_region        = var.region
    retry_policy          = "RETRY_POLICY_DO_NOT_RETRY"
    event_type            = "google.cloud.pubsub.topic.v1.messagePublished"
    pubsub_topic          = google_pubsub_topic.default.id
    service_account_email = data.google_service_account.default.email
  }
}
