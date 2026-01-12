#!/bin/bash
# Check that version.txt matches the git tag version
FILE_VERSION=$(cat version.txt)
GIT_TAG=${GITHUB_REF#refs/tags/v}

if [ "$FILE_VERSION" != "$GIT_TAG" ]; then
  echo "Version mismatch: version.txt ($FILE_VERSION) does not match git tag ($GIT_TAG)"
  exit 1
fi
