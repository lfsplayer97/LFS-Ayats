#!/usr/bin/env python3
"""
File Deletion Agent for GitHub Repository

This script serves as an automated agent to delete files from a local repository.
It operates by scanning the repository directory and deleting all files except
the .git directory, which preserves the repository history.

WARNING: This is a destructive operation. Use with caution!
"""

import os
import sys
import argparse
from pathlib import Path
from typing import List


class FileDeletionAgent:
    """Agent responsible for systematically deleting files from a repository."""
    
    def __init__(self, repo_path: str, dry_run: bool = True):
        """
        Initialize the file deletion agent.
        
        Args:
            repo_path: Path to the repository
            dry_run: If True, only simulate deletion without actually deleting
        """
        self.repo_path = Path(repo_path).resolve()
        self.dry_run = dry_run
        self.excluded_paths = {'.git'}  # Only exclude .git directory
        
    def get_all_files(self) -> List[Path]:
        """
        Get all files in the repository, excluding .git directory.
        
        Returns:
            List of file paths
        """
        all_files = []
        
        for root, dirs, files in os.walk(self.repo_path):
            # Remove excluded directories from search (e.g., .git)
            dirs[:] = [d for d in dirs if d not in self.excluded_paths]
            
            for file in files:
                file_path = Path(root) / file
                all_files.append(file_path)
        
        return all_files
    
    def delete_file(self, file_path: Path) -> bool:
        """
        Delete a single file.
        
        Args:
            file_path: Path to the file to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.dry_run:
                print(f"[DRY RUN] Would delete: {file_path.relative_to(self.repo_path)}")
                return True
            else:
                os.remove(file_path)
                print(f"Deleted: {file_path.relative_to(self.repo_path)}")
                return True
        except (OSError, PermissionError, FileNotFoundError) as e:
            print(f"Error deleting {file_path}: {e}", file=sys.stderr)
            return False
    
    def delete_empty_directories(self) -> int:
        """
        Remove empty directories after file deletion.
        
        Returns:
            Number of directories removed
        """
        count = 0
        for root, dirs, files in os.walk(self.repo_path, topdown=False):
            for dir_name in dirs:
                dir_path = Path(root) / dir_name
                # Skip excluded directories (e.g., .git at any level, including submodules)
                if dir_name in self.excluded_paths:
                    continue
                try:
                    # Check if directory is empty (more efficient than any())
                    if next(dir_path.iterdir(), None) is None:
                        if self.dry_run:
                            print(f"[DRY RUN] Would remove empty directory: {dir_path.relative_to(self.repo_path)}")
                        else:
                            dir_path.rmdir()
                            print(f"Removed empty directory: {dir_path.relative_to(self.repo_path)}")
                        count += 1
                except (OSError, PermissionError) as e:
                    print(f"Error removing directory {dir_path}: {e}", file=sys.stderr)
        
        return count
    
    def execute(self) -> dict:
        """
        Execute the file deletion process.
        
        Returns:
            Dictionary with statistics about the deletion process
        """
        print(f"\n{'='*60}")
        print(f"File Deletion Agent")
        print(f"Repository: {self.repo_path}")
        print(f"Mode: {'DRY RUN (no files will be deleted)' if self.dry_run else 'LIVE (files will be deleted)'}")
        print(f"{'='*60}\n")
        
        # Get all files
        files = self.get_all_files()
        
        if not files:
            print("No files found to delete.")
            return {"files_deleted": 0, "directories_removed": 0}
        
        print(f"Found {len(files)} file(s) to delete.\n")
        
        # Delete files
        deleted_count = 0
        for file_path in files:
            if self.delete_file(file_path):
                deleted_count += 1
        
        print(f"\nDeleted {deleted_count} file(s).")
        
        # Clean up empty directories
        print("\nCleaning up empty directories...")
        dirs_removed = self.delete_empty_directories()
        print(f"Removed {dirs_removed} empty directory(ies).")
        
        return {
            "files_deleted": deleted_count,
            "directories_removed": dirs_removed
        }


def confirm_deletion() -> bool:
    """
    Ask user for confirmation before proceeding with deletion.
    
    Returns:
        True if user confirms, False otherwise
    """
    print("\n" + "!"*60)
    print("WARNING: This will delete ALL files from the repository!")
    print("This operation cannot be undone!")
    print("!"*60 + "\n")
    
    response = input("Are you absolutely sure you want to proceed? (yes/no): ")
    return response.lower() == 'yes'


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="File Deletion Agent - Systematically delete files from a repository",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run (default) - see what would be deleted without deleting
  python delete_files_agent.py /path/to/repo

  # Actually delete files (requires confirmation)
  python delete_files_agent.py /path/to/repo --execute

  # Skip confirmation prompt (dangerous!)
  python delete_files_agent.py /path/to/repo --execute --force
        """
    )
    
    parser.add_argument(
        'repo_path',
        nargs='?',
        default='.',
        help='Path to the repository (default: current directory)'
    )
    
    parser.add_argument(
        '--execute',
        action='store_true',
        help='Actually delete files (default is dry run)'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Skip confirmation prompt (use with caution!)'
    )
    
    args = parser.parse_args()
    
    # Validate repository path
    repo_path = Path(args.repo_path).resolve()
    if not repo_path.exists():
        print(f"Error: Repository path does not exist: {repo_path}", file=sys.stderr)
        return 1
    
    # Check if it's a git repository
    git_dir = repo_path / '.git'
    if not git_dir.exists():
        print(f"Warning: {repo_path} does not appear to be a git repository")
        if not args.force:
            response = input("Continue anyway? (yes/no): ")
            if response.lower() != 'yes':
                return 0
        else:
            print("Continuing anyway (--force flag set)...")
    
    # Determine if this is a dry run
    dry_run = not args.execute
    
    # Request confirmation if not in dry run mode and not forced
    if not dry_run and not args.force:
        if not confirm_deletion():
            print("Operation cancelled.")
            return 0
    
    # Create and execute the agent
    agent = FileDeletionAgent(repo_path, dry_run=dry_run)
    results = agent.execute()
    
    print(f"\n{'='*60}")
    print("Summary:")
    print(f"  Files deleted: {results['files_deleted']}")
    print(f"  Directories removed: {results['directories_removed']}")
    print(f"{'='*60}\n")
    
    if dry_run:
        print("This was a DRY RUN. No files were actually deleted.")
        print("To actually delete files, run with --execute flag.")
    else:
        print("Operation completed successfully!")
        print("\nNext steps:")
        print("  1. Review the changes with: git status")
        print("  2. Commit the changes with: git add -A && git commit -m 'Delete all files'")
        print("  3. Push to GitHub with: git push")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
