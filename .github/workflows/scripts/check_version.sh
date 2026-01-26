#!/bin/bash
# Check that VERSION (package tag) matches OIDN_VERSION by major.minor.patch.
#
# VERSION may be like:
#   - 2.4.1
#   - 2.4.1.x   (where x is an extra numeric segment, e.g. 2.4.1.1)
# OIDN_VERSION must be like:
#   - 2.4.1

set -euo pipefail

VERSION="${VERSION:-}"
OIDN_VERSION="${OIDN_VERSION:-}"

if [[ -z "${VERSION}" || -z "${OIDN_VERSION}" ]]; then
  echo "Missing required env: VERSION='${VERSION:-}', OIDN_VERSION='${OIDN_VERSION:-}'" >&2
  exit 1
fi

extract_three() {
  local v="$1"
  if [[ "$v" =~ ^([0-9]+)\.([0-9]+)\.([0-9]+) ]]; then
    echo "${BASH_REMATCH[1]}.${BASH_REMATCH[2]}.${BASH_REMATCH[3]}"
    return 0
  fi
  return 1
}

if ! [[ "${OIDN_VERSION}" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "Invalid OIDN_VERSION format: '${OIDN_VERSION}' (expected N.N.N)" >&2
  exit 1
fi

VERSION_THREE="$(extract_three "${VERSION}")" || {
  echo "Invalid VERSION format: '${VERSION}' (expected N.N.N or N.N.N.x)" >&2
  exit 1
}

if [[ "${VERSION_THREE}" != "${OIDN_VERSION}" ]]; then
  echo "Version mismatch: VERSION '${VERSION}' (=> ${VERSION_THREE}) != OIDN_VERSION '${OIDN_VERSION}'" >&2
  exit 1
fi

echo "Version OK: VERSION '${VERSION}' matches OIDN_VERSION '${OIDN_VERSION}' by major.minor.patch"
