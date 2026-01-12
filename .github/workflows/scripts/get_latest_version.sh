#!/bin/bash
set -euo pipefail

# Get latest local tag starting with 'v' by time and write VERSION
# into $GITHUB_ENV (mirrors: echo "VERSION=${GITHUB_REF#refs/tags/v}" >> $GITHUB_ENV)

latest_tag=$(git for-each-ref \
	--sort=-creatordate \
	--format '%(refname:short)' \
	'refs/tags/v*' | head -n1 || true)

if [[ -z "${latest_tag}" ]]; then
	echo "No local tags starting with 'v' found." >&2
	exit 1
fi

version_no_v="${latest_tag#v}"

if [[ -n "${GITHUB_ENV:-}" ]]; then
	echo "VERSION=${version_no_v}" >> "$GITHUB_ENV"
	echo "Set VERSION=${version_no_v} from tag ${latest_tag}" >&2
else
	# Fallback for local runs
	echo "VERSION=${version_no_v}"
fi

