#!/bin/bash

# Script to generate specs.md from description.md using sublang CLI

# Check if description.md exists
if [ ! -f "description.md" ]; then
    echo "Error: description.md not found"
    exit 1
fi

echo "Generating specs from description.md..."

# Read the content of description.md
DESCRIPTION=$(cat description.md)

# Create a temporary file to capture the full output
TEMP_OUTPUT=$(mktemp)

# Call sublang with the description
# - Add two empty lines after the content to signal end of input
# - Send 'quit' to exit the interactive session
# - Capture all output to temp file
{
    echo "$DESCRIPTION"
    echo ""
    echo ""
    echo "quit"
} | sublang > "$TEMP_OUTPUT" 2>&1

# Extract only the bot's response (between "Bot: (Working on it...)" and "(Intent: DESIGN_SPECS)")
# This removes the initialization messages and prompts
sed -n '/^Bot: (Working on it...)/,/^(Intent: DESIGN_SPECS)/p' "$TEMP_OUTPUT" | \
    sed '1d;$d' > specs.md

# Clean up temp file
rm -f "$TEMP_OUTPUT"

# Check if specs.md has content
if [ -s "specs.md" ]; then
    echo "Successfully generated specs.md"
else
    echo "Error: Failed to generate specs.md or output was empty"
    exit 1
fi