#!/usr/bin/env python3
"""
Test script for the Enhanced Auto-Committer plugins.
This script demonstrates how to use the auto-committer with plugins.
"""

import os
import sys
import time
import argparse
from git import Repo
from auto_committer import EnhancedAutoCommitter

def create_test_file(repo_path, filename, content):
    """Create a test file in the repository."""
    file_path = os.path.join(repo_path, filename)
    with open(file_path, 'w') as f:
        f.write(content)
    print(f"Created test file: {filename}")
    return file_path

def create_test_repo(repo_path):
    """Create a test repository if it doesn't exist."""
    if not os.path.exists(repo_path):
        os.makedirs(repo_path)
        repo = Repo.init(repo_path)
        print(f"Initialized test repository at {repo_path}")
    else:
        repo = Repo(repo_path)
        print(f"Using existing repository at {repo_path}")
    
    # Create a .gitignore file
    gitignore_path = os.path.join(repo_path, '.gitignore')
    if not os.path.exists(gitignore_path):
        with open(gitignore_path, 'w') as f:
            f.write("__pycache__/\n*.pyc\n.env\n")
        repo.index.add(['.gitignore'])
        repo.index.commit("Add .gitignore")
        print("Added .gitignore file")
    
    return repo

def create_test_config(repo_path, config_path, enabled_plugins=None):
    """Create a test configuration file."""
    if enabled_plugins is None:
        enabled_plugins = ['smart_commit_message', 'code_quality_notes']
    
    config_content = f"""
repository:
  path: "{repo_path}"
  branch: "main"
  remote: "origin"

scheduling:
  enabled: false

file_monitoring:
  enabled: false

commit_behavior:
  min_files_for_commit: 1
  max_files_per_commit: 10

security:
  scan_for_secrets: false

plugins:
  enabled:
"""
    
    for plugin in enabled_plugins:
        config_content += f"    - {plugin}\n"
    
    with open(config_path, 'w') as f:
        f.write(config_content)
    
    print(f"Created test configuration at {config_path}")

def run_test(repo_path, config_path, test_files):
    """Run the auto-committer with the test files."""
    # Create the auto-committer
    auto_committer = EnhancedAutoCommitter(config_path)
    
    # Create test files
    for filename, content in test_files.items():
        create_test_file(repo_path, filename, content)
    
    # Attempt to commit
    print("\nAttempting to commit changes...")
    result = auto_committer.attempt_commit()
    
    if result:
        print("✅ Commit successful!")
    else:
        print("❌ Commit failed!")
    
    return result

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Test the Enhanced Auto-Committer plugins')
    parser.add_argument('--repo', default='./test_repo', help='Path to the test repository')
    parser.add_argument('--config', default='./test_config.yaml', help='Path to the test configuration file')
    parser.add_argument('--plugins', nargs='+', default=['smart_commit_message', 'code_quality_notes'], 
                        help='Plugins to enable')
    args = parser.parse_args()
    
    # Create test repository
    repo = create_test_repo(args.repo)
    
    # Create test configuration
    create_test_config(args.repo, args.config, args.plugins)
    
    # Define test files
    test_files = {
        'test_feature.py': """
def new_feature():
    # This is a new feature
    for i in range(1000):
        for j in range(1000):
            for k in range(1000):
                # This is a complex nested loop
                pass
    
    # TODO: Optimize this function
    return True
""",
        'test_bugfix.py': """
def fix_bug():
    # This is a bug fix
    if some_condition:
        # FIXME: This is a temporary fix
        return 12345  # Magic number
    
    return False
""",
        'test_refactor.py': """
def refactor_code():
    # This is a refactoring
    old_text = "This is a very long string that should be replaced with a constant or variable"
    new_text = old_text.replace("old_text", "new_text")
    
    # Commented code
    # if condition:
    #     do_something()
    
    return new_text
"""
    }
    
    # Run the test
    run_test(args.repo, args.config, test_files)
    
    print("\nTest completed!")
    print(f"Repository: {args.repo}")
    print(f"Configuration: {args.config}")
    print(f"Enabled plugins: {', '.join(args.plugins)}")

if __name__ == '__main__':
    main() 