output "lab_hosts" {
  description = "Name -> IP (without prefix) for building the Ansible inventory"
  value       = { for name, vm in var.vms : name => split("/", vm.ip_cidr)[0] }
}
