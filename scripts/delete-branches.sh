#!/bin/bash

# Script to delete all branches except main
# Usage: ./scripts/delete-branches.sh
# 
# This script safely deletes remote branches with confirmation prompts.
# Protected branches: main, master

set -euo pipefail

# Configuration
PROTECTED_BRANCHES=("main" "master")
DRY_RUN=false

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

is_protected_branch() {
    local branch="$1"
    for protected in "${PROTECTED_BRANCHES[@]}"; do
        if [[ "$branch" == "$protected" ]]; then
            return 0
        fi
    done
    return 1
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [--dry-run]"
            echo ""
            echo "Options:"
            echo "  --dry-run    Show what would be deleted without actually deleting"
            echo "  --help       Show this help message"
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Main script
log_warning "This script will delete ALL remote branches except: ${PROTECTED_BRANCHES[*]}"

if [ "$DRY_RUN" = true ]; then
    log_info "Running in DRY RUN mode - no branches will be deleted"
fi

echo ""
read -rp "Are you sure you want to continue? (yes/no): " confirmation

if [ "$confirmation" != "yes" ]; then
    log_info "Aborted."
    exit 0
fi

# Fetch all remote branches
log_info "Fetching remote branches..."
git fetch --all --prune || {
    log_error "Failed to fetch branches"
    exit 1
}

# Get list of remote branches
log_info "Getting list of branches..."
branches=()
while IFS= read -r branch; do
    # Clean branch name
    branch=$(echo "$branch" | sed 's/origin\///' | tr -d ' ')
    
    # Skip if protected
    if is_protected_branch "$branch"; then
        log_info "Skipping protected branch: $branch"
        continue
    fi
    
    branches+=("$branch")
done < <(git branch -r | grep -v '\->' | grep -v 'HEAD')

if [ ${#branches[@]} -eq 0 ]; then
    log_info "No branches to delete."
    exit 0
fi

# Show branches to be deleted
echo ""
log_warning "The following ${#branches[@]} branches will be deleted:"
printf '%s\n' "${branches[@]}"
echo ""

if [ "$DRY_RUN" = true ]; then
    log_info "DRY RUN complete. No branches were deleted."
    exit 0
fi

read -rp "Type 'DELETE' to confirm: " final_confirmation

if [ "$final_confirmation" != "DELETE" ]; then
    log_info "Aborted."
    exit 0
fi

# Delete branches
deleted_count=0
failed_count=0

for branch in "${branches[@]}"; do
    log_info "Deleting branch: $branch"
    if git push origin --delete "$branch" 2>&1; then
        ((deleted_count++))
    else
        log_warning "Failed to delete: $branch"
        ((failed_count++))
    fi
done

echo ""
log_info "Branch deletion complete!"
log_info "Deleted: $deleted_count"
if [ $failed_count -gt 0 ]; then
    log_warning "Failed: $failed_count"
fi
