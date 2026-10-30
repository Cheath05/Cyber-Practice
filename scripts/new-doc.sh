#!/usr/bin/env bash
# Create a deliverable in a project from a template.
# Usage: scripts/new-doc.sh <project-folder> <template-name> [suffix]
#   scripts/new-doc.sh 01-lab-foundation network-design
#   scripts/new-doc.sh 08-soc-detection-engineering detection-rule kerberoasting
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <project-folder> <template-name> [suffix]" >&2
  echo "Projects:  $(find "$repo_root/projects" -mindepth 1 -maxdepth 1 -type d -printf '%f ' | sort)" >&2
  echo "Templates: $(find "$repo_root/templates" -maxdepth 1 -name '*.md' ! -name README.md -printf '%f ' | sed 's/\.md//g')" >&2
  exit 1
fi

project="${1%/}"
template="${2%.md}"
suffix="${3:-}"

src="$repo_root/templates/$template.md"
dest_dir="$repo_root/projects/$project/deliverables"
name="$template${suffix:+-$suffix}.md"
dest="$dest_dir/$name"

[[ -f "$src" ]] || { echo "No template: $src" >&2; exit 1; }
[[ -d "$repo_root/projects/$project" ]] || { echo "No project: $project" >&2; exit 1; }
mkdir -p "$dest_dir"
if [[ -e "$dest" ]]; then
  echo "Already exists: $dest (not overwriting)" >&2
  exit 1
fi

today="$(date +%F)"
sed "s/YYYY-MM-DD/$today/" "$src" > "$dest"
echo "Created ${dest#"$repo_root"/}"
