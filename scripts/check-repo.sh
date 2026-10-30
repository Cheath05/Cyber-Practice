#!/usr/bin/env bash
# Lint everything in the repo. Install tools with:
#   pip install shellcheck-py yamllint ansible-core
# Usage: scripts/check-repo.sh
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit 1
rc=0
step() { printf '\n\e[1m== %s ==\e[0m\n' "$*"; }

step "shellcheck"
mapfile -t sh_files < <(git ls-files -co --exclude-standard '*.sh')
if command -v shellcheck >/dev/null; then
  shellcheck -x "${sh_files[@]}" && echo "ok (${#sh_files[@]} files)" || rc=1
else echo "shellcheck not installed (skipped)"; fi

step "python compile"
mapfile -t py_files < <(git ls-files -co --exclude-standard '*.py')
python3 -m py_compile "${py_files[@]}" && echo "ok (${#py_files[@]} files)" || rc=1

step "C/C++ syntax"
mapfile -t c_files < <(git ls-files -co --exclude-standard '*.c' '*.cpp')
if command -v g++ >/dev/null; then
  for f in "${c_files[@]}"; do
    if [[ "$f" == *.cpp ]]; then g++ -std=c++17 -Wall -Wextra -fsyntax-only "$f" || rc=1
    else gcc -Wall -Wextra -fsyntax-only "$f" || rc=1; fi
  done
  echo "checked ${#c_files[@]} files"
else echo "g++ not installed (skipped)"; fi

step "yamllint"
mapfile -t yml_files < <(git ls-files -co --exclude-standard '*.yml' '*.yaml')
if command -v yamllint >/dev/null; then
  yamllint -d '{extends: relaxed, rules: {line-length: {max: 140}}}' "${yml_files[@]}" && echo "ok (${#yml_files[@]} files)" || rc=1
else echo "yamllint not installed (skipped)"; fi

step "docker compose config"
mapfile -t compose_files < <(git ls-files -co --exclude-standard '*docker-compose.yml' '*compose.yaml')
if docker compose version >/dev/null 2>&1; then
  for f in "${compose_files[@]}"; do docker compose -f "$f" config -q || { echo "invalid: $f"; rc=1; }; done
  echo "checked ${#compose_files[@]} files"
else echo "docker compose not installed (skipped)"; fi

step "relative markdown links"
python3 scripts/check_links.py || rc=1

step "secrets scan (heuristic)"
if git ls-files -co --exclude-standard | xargs grep -nIE 'BEGIN (RSA|OPENSSH|EC) PRIVATE KEY|PrivateKey *= *[A-Za-z0-9+/]{43}=' 2>/dev/null; then
  echo "Possible secret found above!"; rc=1
else echo "ok"; fi

exit "$rc"
