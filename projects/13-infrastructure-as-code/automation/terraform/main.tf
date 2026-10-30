resource "proxmox_virtual_environment_vm" "lab" {
  for_each = var.vms

  name      = each.key
  node_name = var.node_name
  vm_id     = each.value.vmid
  tags      = ["lab", "terraform"]

  clone {
    vm_id = var.template_id
    full  = false # linked clone: only stores differences from the template
  }

  agent {
    enabled = true
  }

  cpu {
    cores = each.value.cores
    type  = "host"
  }

  memory {
    dedicated = each.value.memory
    floating  = each.value.balloon # balloon minimum; 0 disables ballooning (e.g. Wazuh)
  }

  disk {
    datastore_id = var.datastore
    interface    = "scsi0"
    size         = each.value.disk_gb
  }

  network_device {
    bridge  = "vmbr1"
    vlan_id = each.value.vlan == 0 ? null : each.value.vlan
  }

  initialization {
    datastore_id = var.datastore
    ip_config {
      ipv4 {
        address = each.value.ip_cidr
        gateway = each.value.gateway
      }
    }
    dns {
      servers = [each.value.gateway]
    }
    user_account {
      username = "labadmin"
      keys     = [trimspace(var.ssh_public_key)]
    }
  }
}
