terraform {
  required_version = ">= 1.5.0"
  required_providers {
    proxmox = {
      source = "bpg/proxmox"
      # Pin to the version you test with (see the registry for the latest), e.g. "~> 0.70"
      version = ">= 0.60.0"
    }
  }
}
