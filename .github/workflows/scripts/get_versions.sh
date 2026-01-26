#!/bin/bash
# configured oidn version
OIDN_VERSION=$(cat oidn_version.txt)
# pyoidn version tag
GIT_TAG=${GITHUB_REF#refs/tags/v}

echo "VERSION=$GIT_TAG" >> $GITHUB_ENV
echo "OIDN_VERSION=$OIDN_VERSION" >> $GITHUB_ENV