#!/bin/bash

# Create Issues from Requirements Skill - Shell Wrapper
# Integrates with OpenCode CLI

set -e

# Get the directory where this script is located
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Run the Node.js script with all arguments
node "$SKILL_DIR/create-issues.js" "$@"
