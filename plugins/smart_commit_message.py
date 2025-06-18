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
    
    def _analyze_file_types(self, files: List[str]) -> Dict[str, int]:
        """Analyze the types of files that were changed."""
        file_types = {}
        
        for file_path in files:
            for file_type, patterns in self.file_type_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, file_path):
                        file_types[file_type] = file_types.get(file_type, 0) + 1
                        break
        
        return file_types
    
    def _generate_change_context(self, files: List[str], repo: Repo) -> Dict:
        """Generate context about the changes."""
        context = {
            'file_types': self.file_types,
            'total_files': len(files),
            'file_extensions': self._get_file_extensions(files),
            'is_feature': self._is_feature_change(files),
            'is_bugfix': self._is_bugfix_change(files),
            'is_refactor': self._is_refactor_change(files),
        }
        
        return context
    
    def _get_file_extensions(self, files: List[str]) -> Dict[str, int]:
        """Get the distribution of file extensions in the changes."""
        extensions = {}
        
        for file_path in files:
            _, ext = os.path.splitext(file_path)
            if ext:
                extensions[ext] = extensions.get(ext, 0) + 1
        
        return extensions
    
    def _is_feature_change(self, files: List[str]) -> bool:
        """Check if the changes appear to be a new feature."""
        feature_indicators = [
            r'feature', r'add', r'new', r'create', r'implement',
            r'enhance', r'improve', r'upgrade'
        ]
        
        return self._check_file_patterns(files, feature_indicators)
    
    def _is_bugfix_change(self, files: List[str]) -> bool:
        """Check if the changes appear to be a bug fix."""
        bugfix_indicators = [
            r'fix', r'bug', r'issue', r'error', r'fail',
            r'correct', r'repair', r'resolve'
        ]
        
        return self._check_file_patterns(files, bugfix_indicators)
    
    def _is_refactor_change(self, files: List[str]) -> bool:
        """Check if the changes appear to be a refactoring."""
        refactor_indicators = [
            r'refactor', r'restructure', r'reorganize', r'clean',
            r'optimize', r'improve', r'enhance'
        ]
        
        return self._check_file_patterns(files, refactor_indicators)
    
    def _check_file_patterns(self, files: List[str], patterns: List[str]) -> bool:
        """Check if any file matches the given patterns."""
        for file_path in files:
            for pattern in patterns:
                if re.search(pattern, file_path, re.IGNORECASE):
                    return True
        return False
    
    def _enhance_commit_message(self, original_message: str) -> str:
        """Enhance the commit message with additional context."""
        if not hasattr(self, 'change_context'):
            return original_message
            
        context = self.change_context
        
        # Don't enhance if the message already has detailed information
        if len(original_message.split('\n')) > 2:
            return original_message
            
        # Create enhanced message
        enhanced_message = original_message.rstrip()
        
        # Add file type information
        if context['file_types']:
            file_types_str = ", ".join([f"{k}: {v}" for k, v in context['file_types'].items()])
            enhanced_message += f"\n\nChanged file types: {file_types_str}"
        
        # Add change type information
        change_types = []
        if context['is_feature']:
            change_types.append("feature")
        if context['is_bugfix']:
            change_types.append("bugfix")
        if context['is_refactor']:
            change_types.append("refactor")
            
        if change_types:
            enhanced_message += f"\nChange type: {', '.join(change_types)}"
        
        return enhanced_message 