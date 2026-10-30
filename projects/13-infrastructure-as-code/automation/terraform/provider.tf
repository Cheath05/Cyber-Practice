provider "proxmox" {
  endpoint  = var.pm_endpoint
  api_token = var.pm_api_token # or leave unset and export PROXMOX_VE_API_TOKEN
  # The lab uses Proxmox's self-signed certificate. After Project 12, install a cert from your
  # internal CA on the Proxmox GUI and set this to false.
  insecure = true
}
