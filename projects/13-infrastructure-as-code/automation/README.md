# ⚠️ Solution: use only if stuck

| Path | What it does |
|---|---|
| `terraform/` | bpg/proxmox provider config + a `for_each` VM resource cloning template 9000 into lab VLANs |
| `ansible/` | Inventory, config and `site.yml` baseline (UFW, SSH hardening, auditd, auto-updates, banner) + Docker role |
| `python/tf_to_inventory.py` | Python exercise: `terraform output -json` → Ansible inventory |
| `github-actions-lint.yml` | Copy to `.github/workflows/lint.yml` in your repo for CI |

Secrets never go in these files: the API token lives in an untracked `terraform.tfvars` (see
`terraform.tfvars.example`) or the `PROXMOX_VE_API_TOKEN` environment variable.
