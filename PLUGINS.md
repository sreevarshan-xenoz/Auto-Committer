# Enhanced Auto-Committer Plugins

The Enhanced Auto-Committer includes a powerful plugin system that allows you to extend its functionality. This document explains how to use existing plugins and how to develop your own.

## Using Plugins

### Enabling Plugins

Plugins are enabled in the `auto_committer_config.yaml` file under the `plugins` section:

```yaml
plugins:
  enabled:
    - smart_commit_message
    # - code_quality_notes
    # - diff_viewer
    # - bug_risk_score
    # - file_prioritization
    # - commit_karma
    # - mobile_integration
    # - git_visualizer
    # - intention_aware
    # - branch_management
```

Simply uncomment the plugins you want to enable.

### Available Plugins

The Enhanced Auto-Committer comes with several built-in plugins:

1. **Smart Commit Message** (`smart_commit_message`): Enhances commit messages with additional context based on file changes.
2. **Code Quality Notes** (`code_quality_notes`): Analyzes code changes and adds quality notes to commit messages.
3. **Diff Viewer** (`diff_viewer`): Provides a visual representation of changes in the commit.
4. **Bug Risk Score** (`bug_risk_score`): Calculates a risk score for potential bugs in the changes.
5. **File Prioritization** (`file_prioritization`): Prioritizes files for review based on importance.
6. **Commit Karma** (`commit_karma`): Tracks and rewards good commit practices.
7. **Mobile Integration** (`mobile_integration`): Sends notifications to mobile devices.
8. **Git Visualizer** (`git_visualizer`): Creates visualizations of the commit history.
9. **Intention Aware** (`intention_aware`): Analyzes developer intentions from commit messages.
10. **Branch Management** (`branch_management`): Helps manage branch creation and merging.

## Developing Plugins

### Plugin Structure

All plugins must inherit from the `BasePlugin` class and implement at least one of the hook methods. Here's a basic plugin structure:

```python
from plugins.base import BasePlugin

class MyPlugin(BasePlugin):
    """Description of what the plugin does."""
    
    name = "MyPlugin"
    
    def __init__(self, config=None):
        super().__init__(config)
        # Initialize your plugin here
    
    def pre_commit(self, repo, changed_files):
        """Hook to run before a commit. Can modify commit message or files."""
        # Your code here
    
    def post_commit(self, repo, commit):
        """Hook to run after a commit is created."""
        # Your code here
    
    def on_push(self, repo, commit):
        """Hook to run after a push to remote."""
        # Your code here
    
    def on_error(self, error):
        """Hook to handle errors in the commit process."""
        # Your code here
```

### Plugin Hooks

The Enhanced Auto-Committer provides several hooks that your plugin can implement:

1. **pre_commit(repo, changed_files)**: Called before a commit is created. You can use this to:
   - Analyze the changes
   - Modify files before they are committed
   - Prepare data for post-commit processing

2. **post_commit(repo, commit)**: Called after a commit is created but before it is pushed. You can use this to:
   - Enhance the commit message
   - Add metadata to the commit
   - Perform additional analysis

3. **on_push(repo, commit)**: Called after a commit is pushed to the remote repository. You can use this to:
   - Send notifications
   - Update external systems
   - Trigger CI/CD pipelines

4. **on_error(error)**: Called when an error occurs during the commit process. You can use this to:
   - Log errors
   - Send error notifications
   - Attempt to recover from errors

### Creating a New Plugin

To create a new plugin:

1. Create a new Python file in the `plugins` directory (e.g., `my_plugin.py`)
2. Implement your plugin class as shown above
3. Add your plugin to the `enabled` list in `auto_committer_config.yaml`

### Example: Smart Commit Message Plugin

Here's an example of the Smart Commit Message plugin:

```python
import os
import re
from typing import List, Dict, Optional
from git import Repo, Commit
from .base import BasePlugin

class SmartCommitMessagePlugin(BasePlugin):
    """Plugin that enhances commit messages with additional context based on file changes."""
    
    name = "SmartCommitMessage"
    
    def __init__(self, config=None):
        super().__init__(config)
        self.file_type_patterns = {
            'frontend': [r'\.(js|jsx|ts|tsx|css|scss|html|vue)$'],
            'backend': [r'\.(py|java|c|cpp|go|rb|php)$'],
            'database': [r'\.(sql|db|sqlite)$'],
            'config': [r'\.(yaml|yml|json|xml|ini|conf|config)$'],
            'test': [r'\.(test|spec)\.(js|py|java)$', r'test_.*\.py$'],
            'documentation': [r'\.(md|rst|txt|doc|docx)$'],
        }
        
    def pre_commit(self, repo: Repo, changed_files: List[str]) -> None:
        """Analyze changed files and store context for post-commit enhancement."""
        self.changed_files = changed_files
        self.file_types = self._analyze_file_types(changed_files)
        self.change_context = self._generate_change_context(changed_files, repo)
        
    def post_commit(self, repo: Repo, commit: Commit) -> None:
        """Enhance the commit message with additional context."""
        if not hasattr(self, 'change_context') or not self.change_context:
            return
            
        # Get the original commit message
        original_message = commit.message
        
        # Create enhanced message
        enhanced_message = self._enhance_commit_message(original_message)
        
        # Only amend if the message has been enhanced
        if enhanced_message != original_message:
            try:
                # Amend the commit with the enhanced message
                repo.git.commit('--amend', '-m', enhanced_message, '--no-edit')
                print(f"Enhanced commit message: {enhanced_message}")
            except Exception as e:
                print(f"Failed to enhance commit message: {e}")
    
    # Helper methods...
```

### Best Practices for Plugin Development

1. **Keep plugins focused**: Each plugin should do one thing well.
2. **Handle errors gracefully**: Always catch and log exceptions in your plugin.
3. **Use configuration**: Allow users to configure your plugin through the config file.
4. **Document your plugin**: Include clear documentation on what your plugin does and how to use it.
5. **Test your plugin**: Ensure your plugin works correctly in different scenarios.

## Advanced Plugin Development

### Accessing Git Repository

Your plugin has access to the Git repository through the `repo` parameter in the hook methods. You can use this to:

- Get commit history
- Access file contents
- Perform Git operations

Example:

```python
def pre_commit(self, repo, changed_files):
    # Get the last commit
    last_commit = repo.head.commit
    
    # Get the diff between the last commit and the current state
    diff = repo.git.diff('HEAD')
    
    # Get the contents of a file
    file_content = repo.git.show(f'HEAD:{changed_files[0]}')
```

### Modifying Files Before Commit

You can modify files before they are committed in the `pre_commit` hook:

```python
def pre_commit(self, repo, changed_files):
    for file_path in changed_files:
        if file_path.endswith('.py'):
            # Read the file
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Modify the content
            modified_content = content.replace('old_text', 'new_text')
            
            # Write the modified content back
            with open(file_path, 'w') as f:
                f.write(modified_content)
```

### Enhancing Commit Messages

You can enhance commit messages in the `post_commit` hook:

```python
def post_commit(self, repo, commit):
    # Get the original commit message
    original_message = commit.message
    
    # Create an enhanced message
    enhanced_message = f"{original_message}\n\nEnhanced by MyPlugin"
    
    # Amend the commit with the enhanced message
    repo.git.commit('--amend', '-m', enhanced_message, '--no-edit')
```

### Sending Notifications

You can send notifications in the `on_push` hook:

```python
def on_push(self, repo, commit):
    # Send a notification
    import requests
    
    webhook_url = self.config.get('notifications', {}).get('webhook', {}).get('url')
    if webhook_url:
        payload = {
            'text': f'Commit pushed: {commit.message}',
            'commit_id': commit.hexsha,
            'author': commit.author.name
        }
        requests.post(webhook_url, json=payload)
```

## Troubleshooting Plugins

If you encounter issues with plugins:

1. **Check the logs**: The Enhanced Auto-Committer logs plugin errors.
2. **Disable plugins**: Try disabling plugins one by one to identify the problematic plugin.
3. **Check configuration**: Ensure your plugin is correctly configured.
4. **Update plugins**: Make sure you're using the latest version of the plugin.

## Contributing Plugins

We welcome contributions to the Enhanced Auto-Committer plugin ecosystem. To contribute a plugin:

1. Fork the repository
2. Create a new branch for your plugin
3. Implement your plugin
4. Add documentation
5. Submit a pull request

Please ensure your plugin follows the best practices outlined in this document. 