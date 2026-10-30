#!/usr/bin/env bash
# Internal helper used to scaffold a project's WORKLOG.md and deliverables/README.md.
# Usage: scripts/_scaffold.sh <project-folder> "<Project title>" <hours> "<deliverable rows>"
#   deliverable rows: lines of "template|suffix|description" separated by newlines
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
proj="$1"; title="$2"; hours="$3"; rows="$4"
dir="$root/projects/$proj"
mkdir -p "$dir/deliverables"

if [[ ! -f "$dir/WORKLOG.md" ]]; then
  sed -e "s/<Project NN – Name>/$title/" -e "s/Estimate: <N> h/Estimate: $hours h/" \
    "$root/templates/worklog.md" > "$dir/WORKLOG.md"
fi

{
  echo "# Deliverables: $title"
  echo
  echo "Create each document from its template, then fill it in. Tick it off when it's done"
  echo "*and* sanitized (see [documentation guide](../../../docs/documentation-guide.md#sanitizing-before-publishing))."
  echo
  echo "| Done | Document | Create with |"
  echo "|---|---|---|"
  while IFS='|' read -r tpl suffix desc; do
    [[ -z "$tpl" ]] && continue
    cmd="scripts/new-doc.sh $proj $tpl${suffix:+ $suffix}"
    echo "| ☐ | $desc | \`$cmd\` |"
  done <<< "$rows"
  echo
  echo "Screenshots go in \`img/\` next to this file."
} > "$dir/deliverables/README.md"
echo "scaffolded $proj"
