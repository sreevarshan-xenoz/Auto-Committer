#!/usr/bin/env python3
"""
Example script demonstrating how to use the Enhanced Auto-Committer with plugins.
"""

import os
import sys
import argparse
import tempfile
import shutil
from git import Repo
from auto_committer import EnhancedAutoCommitter

def create_test_repo():
    """Create a test repository for demonstration."""
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp(prefix="auto_committer_test_")
    
    # Initialize a Git repository
    repo = Repo.init(temp_dir)
    
    # Create a test file
    test_file = os.path.join(temp_dir, "test.py")
    with open(test_file, "w") as f:
        f.write("""
def hello_world():
    # This is a simple function
    print("Hello, World!")
    
    # TODO: Add more functionality
    
    # This is a complex function with nested control structures
    for i in range(10):
        if i % 2 == 0:
            for j in range(5):
                if j % 2 == 0:
                    print(f"{i} is even and {j} is even")
                else:
                    print(f"{i} is even and {j} is odd")
        else:
            for j in range(5):
                if j % 2 == 0:
                    print(f"{i} is odd and {j} is even")
                else:
                    print(f"{i} is odd and {j} is odd")
    
    # This is a function with a magic number
    return 42  # Magic number
""")
    
    # Add and commit the file
    repo.index.add([test_file])
    repo.index.commit("Initial commit")
    
    return repo, temp_dir

def create_config_file(repo_path, enabled_plugins=None):
    """Create a configuration file for the auto-committer."""
    if enabled_plugins is None:
        enabled_plugins = ["smart_commit_message", "code_quality_notes"]
    
    config_file = os.path.join(repo_path, "auto_committer_config.yaml")
    with open(config_file, "w") as f:
        f.write(f"""
# Enhanced Auto-Committer Configuration

# Repository settings
repository:
  path: "{repo_path}"
  branch: "main"
  remote: "origin"

# Scheduling settings
scheduling:
  enabled: false
  interval: 300  # 5 minutes

# File monitoring settings
file_monitoring:
  enabled: true
  watch_directories: ["."]
  ignore_patterns: [".git", "__pycache__", "*.pyc"]

# Commit behavior settings
commit_behavior:
  commit_message_template: "Auto-commit: {timestamp}"
  max_files_per_commit: 10
  min_commit_interval: 60  # 1 minute

# AI integration settings
ai_integration:
  enabled: false
  openai_api_key: ""
  model: "gpt-3.5-turbo"

# Security settings
security:
  scan_files: true
  secret_patterns: ["password", "api_key", "secret"]
  blocked_extensions: [".pem", ".key", ".crt"]

# Notification settings
notifications:
  email:
    enabled: false
    smtp_server: ""
    smtp_port: 587
    username: ""
    password: ""
    recipients: []
  webhook:
    enabled: false
    url: ""
    events: ["commit", "push"]

# Logging settings
logging:
  level: "INFO"
  file: "auto_committer.log"
  max_size: 10485760  # 10 MB
  backup_count: 5

# Plugin settings
plugins:
  enabled: {enabled_plugins}
""")
    
    return config_file

def run_example(repo_path=None, config_path=None, enabled_plugins=None):
    """Run the example with the specified parameters."""
    # Create a test repository if not provided
    if repo_path is None:
        repo, repo_path = create_test_repo()
    else:
        repo = Repo(repo_path)
    
    # Create a configuration file if not provided
    if config_path is None:
        config_path = create_config_file(repo_path, enabled_plugins)
    
    # Initialize the auto-committer
    auto_committer = EnhancedAutoCommitter(config_path)
    
    # Make a change to the repository
    test_file = os.path.join(repo_path, "test.py")
    with open(test_file, "a") as f:
        f.write("""
# This is a new function
def new_function():
    # This function has a hardcoded string
    message = "This is a very long hardcoded string that should be detected by the code quality plugin"
    print(message)
    
    # This function has a magic number
    return 1000  # Magic number
""")
    
    # Run the auto-committer once
    auto_committer.run_once()
    
    print("Example completed successfully!")
    print(f"Repository path: {repo_path}")
    print(f"Configuration file: {config_path}")
    
    return repo_path

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Example script for Enhanced Auto-Committer with plugins")
    parser.add_argument("--repo", help="Path to the repository")
    parser.add_argument("--config", help="Path to the configuration file")
    parser.add_argument("--plugins", nargs="+", help="List of plugins to enable")
    args = parser.parse_args()
    
    repo_path = run_example(args.repo, args.config, args.plugins)
    
    print("\nTo clean up the test repository, run:")
    print(f"rm -rf {repo_path}")

if __name__ == "__main__":
    main() 