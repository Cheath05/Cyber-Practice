# Terraform for the lab

1. Create a least-privilege token on the Proxmox host (privileges per the
   [bpg/proxmox docs](https://registry.terraform.io/providers/bpg/proxmox/latest/docs) for your
   PVE version; this list works for PVE 8, adjust if `pveum` rejects a name):
   ```bash
   pveum user add terraform@pve
   pveum role add TerraformProv -privs "Datastore.AllocateSpace Datastore.Audit Pool.Allocate Sys.Audit Sys.Console Sys.Modify VM.Allocate VM.Audit VM.Clone VM.Config.CDROM VM.Config.Cloudinit VM.Config.CPU VM.Config.Disk VM.Config.HWType VM.Config.Memory VM.Config.Network VM.Config.Options VM.Migrate VM.PowerMgmt SDN.Use"
   pveum aclmod / -user terraform@pve -role TerraformProv
   pveum user token add terraform@pve tf --privsep 0
   ```
2. `cp terraform.tfvars.example terraform.tfvars` and fill it in (it's git-ignored).
3. `terraform init && terraform plan` → read it → `terraform apply`.
