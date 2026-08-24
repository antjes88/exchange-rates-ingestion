variable "project_id" {
  type        = string
  description = "Name of the Google Project"
}

variable "region" {
  type        = string
  default     = "europe-west2"
  description = "Location for the resources"
}

variable "temp_folder_prefix" {
  description = "Prefix for the temporary folder"
  type        = string
  default     = "temp-cloud-function"
}

variable "cloud_function_name" {
  type        = string
  description = "Name of the Cloud Function"
}

variable "service_account_name" {
  type        = string
  description = "Name of the Cloud Function"
}

variable "function_entry_point" {
  type        = string
  description = "Name of the Cloud Function"
}

variable "zip_file_path" {
  type        = string
  description = "Name of zip file with the Cloud Function code"
}
