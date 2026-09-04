#!/usr/bin/env bash
# Copyright (c) Microsoft Corporation.
# SPDX-License-Identifier: MIT
#
# Restore allowlisted files for an independent GH-300 demo scenario.

set -euo pipefail

readonly EXIT_FAILURE=1
readonly EXIT_USAGE=2

dry_run=false
assume_yes=false
scenario="starter"
scenario_supplied=false

usage() {
  cat <<'EOF'
Usage: scripts/demo-reset.sh [--dry-run] [--yes] [SCENARIO]

Restore a scenario from its immutable Git checkpoint. Changes outside the
scenario allowlist always block the reset. Use --dry-run to inspect actions and
--yes only after reviewing the listed destructive operations.
EOF
}

err() {
  printf 'ERROR: %s\n' "$1" >&2
  exit "${2:-${EXIT_FAILURE}}"
}

require_command() {
  local command_name="$1"
  command -v "${command_name}" &>/dev/null || \
    err "'${command_name}' is required but not installed"
}

parse_arguments() {
  while (( $# > 0 )); do
    case "$1" in
      --dry-run)
        dry_run=true
        ;;
      --yes|-y)
        assume_yes=true
        ;;
      --help|-h)
        usage
        exit 0
        ;;
      --*)
        err "unknown option: $1" "${EXIT_USAGE}"
        ;;
      *)
        if [[ "${scenario_supplied}" == true ]]; then
          err "only one scenario may be specified" "${EXIT_USAGE}"
        fi
        scenario="$1"
        scenario_supplied=true
        ;;
    esac
    shift
  done
}

load_scenario() {
  local repository_root="$1"
  local manifest="$2"
  local selected="$3"
  local guard_script="$4"
  local output
  output="$(python3 "${guard_script}" \
    "${repository_root}" "${manifest}" "${selected}")" || \
    err "could not safely load scenario '${selected}'"
  mapfile -t scenario_config <<<"${output}"
}

parse_scenario_config() {
  checkpoint_ref="${scenario_config[0]:-}"
  checkpoint_commit="${scenario_config[1]:-}"
  restore_paths=()
  generated_paths=()
  local section=""
  local value
  for value in "${scenario_config[@]:2}"; do
    case "${value}" in
      --RESTORE--) section="restore" ;;
      --GENERATED--) section="generated" ;;
      *)
        if [[ "${section}" == "restore" ]]; then
          restore_paths+=("${value}")
        elif [[ "${section}" == "generated" ]]; then
          generated_paths+=("${value}")
        fi
        ;;
    esac
  done
  [[ -n "${checkpoint_ref}" ]] || err "scenario has no checkpoint ref"
  [[ -n "${checkpoint_commit}" ]] || err "scenario has no pinned commit"
  (( ${#restore_paths[@]} > 0 )) || err "scenario has no restore paths"
  (( ${#generated_paths[@]} > 0 )) || err "scenario has no generated paths"
}

show_plan() {
  printf 'Scenario: %s\n' "${scenario}"
  printf 'Checkpoint: %s\n' "${checkpoint_ref}"
  printf 'Pinned commit: %s\n' "${checkpoint_commit}"
  printf 'Restore tracked paths:\n'
  printf '  %s\n' "${restore_paths[@]}"
  printf 'Remove generated paths:\n'
  printf '  %s\n' "${generated_paths[@]}"
}

confirm_reset() {
  if [[ "${assume_yes}" == true ]]; then
    return
  fi
  if [[ ! -t 0 ]]; then
    err "confirmation required; rerun interactively or pass --yes"
  fi
  local answer
  read -r -p "Restore this scenario and remove generated files? [y/N] " answer
  [[ "${answer}" =~ ^[Yy]$ ]] || err "reset cancelled"
}

apply_reset() {
  git restore --source="${checkpoint_commit}" --staged --worktree -- \
    "${restore_paths[@]}"
  git clean -fdx -- "${generated_paths[@]}"
}

main() {
  parse_arguments "$@"
  require_command git
  require_command python3

  local repository_root
  repository_root="$(git rev-parse --show-toplevel 2>/dev/null)" || \
    err "run this command inside a Git repository"
  cd "${repository_root}"

  local script_directory
  script_directory="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
  local guard_script="${script_directory}/reset_guard.py"
  [[ -f "${guard_script}" ]] || err "reset guard not found: ${guard_script}"
  local manifest="${repository_root}/demo/checkpoints.json"
  [[ -f "${manifest}" ]] || err "checkpoint manifest not found: ${manifest}"
  load_scenario \
    "${repository_root}" "${manifest}" "${scenario}" "${guard_script}"
  parse_scenario_config
  show_plan

  if [[ "${dry_run}" == true ]]; then
    printf 'Dry run: no files changed.\n'
    return
  fi

  confirm_reset
  apply_reset
  printf 'Scenario %s restored from %s.\n' \
    "${scenario}" "${checkpoint_ref}"
}

main "$@"