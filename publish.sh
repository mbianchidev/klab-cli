#!/bin/bash

# Have twine installed via "pip install twine" command
# Have file ~/.pypirc with the following content
# [pypi]
#   username = __token__
#   password = [generated-token]

# Define the path to the metadata file (e.g., setup.cfg)
METADATA_FILE="setup.cfg"
# Get the current version from the metadata file
CURRENT_VERSION=$(grep "version =" "$METADATA_FILE" | awk -F" = " '{print $2}')
# Split the version string into major, minor, and patch components
IFS='.' read -ra VERSION_PARTS <<< "$CURRENT_VERSION"
MAJOR="${VERSION_PARTS[0]}"
MINOR="${VERSION_PARTS[1]}"
PATCH="${VERSION_PARTS[2]}"
# Increment the patch version by one
PATCH=$((PATCH + 1))
# Create the new version string
NEW_VERSION="$MAJOR.$MINOR.$PATCH"
# Replace the old version with the new version in the metadata file
sed -i "s/version = $CURRENT_VERSION/version = $NEW_VERSION/" "$METADATA_FILE"
echo "Version incremented to $NEW_VERSION in $METADATA_FILE"

# Define the path to the setup.py file
SETUP_FILE="setup.py"
# Get the current version from the setup.py file (warning: variable name is reused)
CURRENT_VERSION=$(grep "version =" "$SETUP_FILE" | awk -F"'" '{print $2}')
# Split the version string into major, minor, and patch components
IFS='.' read -ra VERSION_PARTS <<< "$CURRENT_VERSION"
MAJOR="${VERSION_PARTS[0]}"
MINOR="${VERSION_PARTS[1]}"
PATCH="${VERSION_PARTS[2]}"
# Increment the patch version by one
PATCH=$((PATCH + 1))
# Create the new version string
NEW_VERSION="$MAJOR.$MINOR.$PATCH"
# Replace the old version with the new version in the setup.py file
sed -i "s/version='$CURRENT_VERSION'/version='$NEW_VERSION'/" "$SETUP_FILE"
echo "Version incremented to $NEW_VERSION in $SETUP_FILE"

python3 -m build && python3 setup.py sdist bdist_wheel && twine upload dist/kubelab_cli-$NEW_VERSION* --verbose

echo "Published version $NEW_VERSION on pipy.org"