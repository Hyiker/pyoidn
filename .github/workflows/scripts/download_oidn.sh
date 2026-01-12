#!/bin/bash

set -euo pipefail

# Expects environment variables:
#   VERSION  - OIDN version (e.g., 2.3.3)
#   ARCH     - Architecture (e.g., x64, x86_64, arm64)
#   PLATFORM - Platform (windows, linux, macos)

VERSION="${VERSION:-}"
ARCH="${ARCH:-}"
PLATFORM="${PLATFORM:-}"

if [[ -z "${VERSION}" || -z "${ARCH}" || -z "${PLATFORM}" ]]; then
  echo "Missing required env: VERSION='${VERSION:-}', ARCH='${ARCH:-}', PLATFORM='${PLATFORM:-}'" >&2
  exit 1
fi

FILENAME="oidn-${VERSION}.${ARCH}.${PLATFORM}"
BASE_URL="https://github.com/RenderKit/oidn/releases/download/v${VERSION}"

echo "Preparing to download OIDN: version=${VERSION}, arch=${ARCH}, platform=${PLATFORM}" 

mkdir -p pyoidn/oidn

if [[ "${PLATFORM}" == "windows" ]]; then
  ARCHIVE="${FILENAME}.zip"
  echo "Downloading ${ARCHIVE}..."
  curl -L -o oidn.zip "${BASE_URL}/${ARCHIVE}"
  7z x oidn.zip
else
  ARCHIVE="${FILENAME}.tar.gz"
  echo "Downloading ${ARCHIVE}..."
  curl -L -o oidn.tar.gz "${BASE_URL}/${ARCHIVE}"
  tar -xzf oidn.tar.gz
fi

echo "Copying OIDN binaries to pyoidn/oidn/..."
cp -r "${FILENAME}/bin" pyoidn/oidn/
cp -r "${FILENAME}/lib" pyoidn/oidn/

echo "Download and extraction complete. Contents in pyoidn/oidn:"
ls -la pyoidn/oidn
