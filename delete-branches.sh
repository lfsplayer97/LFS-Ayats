#!/bin/bash

# Script to delete all branches except main
# Usage: ./delete-branches.sh

set -e

echo "This script will delete ALL branches except 'main'"
echo "Are you sure you want to continue? (yes/no)"
read -r confirmation

if [ "$confirmation" != "yes" ]; then
    echo "Aborted."
    exit 0
fi

# Fetch all branches
echo "Fetching all remote branches..."
git fetch --all --prune

# Get list of all remote branches except main
echo "Getting list of branches to delete..."
branches=$(git branch -r | grep -v '\->' | grep -v 'origin/main' | sed 's/origin\///' | tr -d ' ')

if [ -z "$branches" ]; then
    echo "No branches to delete."
    exit 0
fi

echo "The following branches will be deleted:"
echo "$branches"
echo ""
echo "Type 'DELETE' to confirm:"
read -r final_confirmation

if [ "$final_confirmation" != "DELETE" ]; then
    echo "Aborted."
    exit 0
fi

# Delete each branch
for branch in $branches; do
    echo "Deleting branch: $branch"
    git push origin --delete "$branch" 2>&1 || echo "Warning: Failed to delete $branch"
done

echo ""
echo "Branch deletion complete!"
echo "Deleted branches: $(echo "$branches" | wc -l)"
