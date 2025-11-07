# LFS-Ayats

This repository contains tools and workflows for managing branches.

## Branch Management

### Deleting All Branches

There are two ways to delete all branches (except `main`):

#### Option 1: Using the Shell Script

Run the provided script:

```bash
./delete-branches.sh
```

The script will:
1. Fetch all remote branches
2. List all branches that will be deleted
3. Ask for confirmation before proceeding
4. Delete all branches except `main`

#### Option 2: Using GitHub Actions Workflow

1. Go to the "Actions" tab in the GitHub repository
2. Select the "Delete All Branches" workflow
3. Click "Run workflow"
4. Type `DELETE ALL BRANCHES` in the confirmation field
5. Click "Run workflow" to execute

#### Manual Branch Deletion

To manually delete branches one by one:

```bash
# Delete a local branch
git branch -d branch-name

# Delete a remote branch
git push origin --delete branch-name
```

### Current Branches

The following branches currently exist in this repository:
- `main` (default branch)
- `copilot/delete-all-branches`
- `copilot/improve-html-file-functionality`
- `codex/add-internationalization-support-to-overlay`
- `codex/add-internationalization-support-to-overlay-l3kfwn`
- `codex/add-internationalization-support-to-overlay-xppf8q`
- `web`

## Safety Notes

- The `main` branch is protected and will not be deleted
- Always review the list of branches before confirming deletion
- Deleted branches cannot be easily recovered
- Make sure you have backed up any important work before deleting branches
