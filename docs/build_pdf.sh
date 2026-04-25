#!/bin/bash

set -euo pipefail

# Check if pandoc is installed
if ! command -v pandoc &> /dev/null; then
    echo "Pandoc could not be found. Please install it to continue."
    exit 1
fi

# Create a temporary working directory
WORKDIR=$(mktemp -d)

# Copy necessary markdown files to the temporary directory
cp README.md SETUP.md TESTING.md ConfigurationStep.md "$WORKDIR/"

# Normalize line endings
find "$WORKDIR" -type f -exec dos2unix {} \;

# Run pandoc to generate the PDF
pandoc "$WORKDIR/README.md" "$WORKDIR/SETUP.md" "$WORKDIR/TESTING.md" "$WORKDIR/ConfigurationStep.md" -o docs/Email_SPAM_DETECTOR_USING_ML.pdf --title="Email Spam Detector Using ML" --toc

# Clean up
rm -rf "$WORKDIR"