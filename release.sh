#!/bin/bash

# Enhanced Auto-Committer Release Script
# This script helps create a new release on GitHub

VERSION="0.1.0-alpha"
RELEASE_DATE=$(date +"%Y-%m-%d")
RELEASE_TITLE="Enhanced Auto-Committer v$VERSION (Alpha)"
RELEASE_BRANCH="main"
RELEASE_NOTES="## What's New in Alpha Release

This is the initial alpha release of the Enhanced Auto-Committer. Key features include:

- Core auto-committing functionality
- Real-time file monitoring
- Configurable scheduling
- Security scanning for sensitive data
- AI-powered commit message generation (optional)
- Multiple deployment options (direct, Docker, system service)
- Comprehensive logging
- Quick start scripts for Windows and Unix-like systems

## Installation

See the README.md file for detailed installation instructions.

## Known Issues

- This is an alpha release and may contain bugs
- Some advanced features may not be fully tested
- Performance may vary depending on repository size

## Feedback

Please report any issues or suggestions on the GitHub repository."

# Update version in setup.py
sed -i "s/version=\".*\"/version=\"$VERSION\"/" setup.py

# Update CHANGELOG.md with release date
sed -i "s/## \[$VERSION\] - .*/## \[$VERSION\] - $RELEASE_DATE/" CHANGELOG.md

# Create a release commit
git add setup.py CHANGELOG.md
git commit -m "Prepare for $VERSION release"

# Create a tag
git tag -a "v$VERSION" -m "Release v$VERSION"

# Push changes and tag
git push origin $RELEASE_BRANCH
git push origin "v$VERSION"

echo "Release preparation complete!"
echo "Now go to https://github.com/sreevarshan-xenoz/Auto-Committer/releases/new"
echo "Select the v$VERSION tag"
echo "Set the release title to: $RELEASE_TITLE"
echo "Add the following release notes:"
echo ""
echo "$RELEASE_NOTES"
echo ""
echo "Then publish the release." 