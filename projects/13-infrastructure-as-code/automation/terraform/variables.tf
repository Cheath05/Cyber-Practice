variable "pm_endpoint" {
  description = "Proxmox API URL, e.g. https://192.168.1.10:8006/"
  type        = string
}

variable "pm_api_token" {
  description = "API token as 'terraform@pve!tf=<secret>'. Keep it out of Git."
  type        = string
  sensitive   = true
  default     = null
}

variable "node_name" {
  description = "Proxmox node name (Datacenter tree)"
  type        = string
  default     = "pve"
}

variable "template_id" {
  description = "VMID of the Ubuntu cloud-init template (Project 01)"
  type        = number
  default     = 9000
}

variable "datastore" {
  description = "Storage for VM disks and cloud-init drives"
  type        = string
  default     = "local-lvm"
}

variable "ssh_public_key" {
  description = "Public key for the labadmin cloud-init user"
  type        = string
}

variable "vms" {
  description = "Lab VMs to manage. vlan = 0 means untagged (LAB-MGMT)."
  type = map(object({
    vmid    = number
    vlan    = number
    ip_cidr = string
    gateway = string
    memory  = number
    balloon = number
    cores   = number
    disk_gb = number
  }))
}
