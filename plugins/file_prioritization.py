import os
import re
from typing import List, Dict, Optional, Tuple
from git import Repo, Commit
from .base import BasePlugin

class FilePrioritizationPlugin(BasePlugin):
    """Plugin that prioritizes files for review based on their importance and the types of changes made."""
    
    name = "FilePrioritization"
    
    def __init__(self, config=None):
        super().__init__(config)
        # Define file importance factors
        self.importance_factors = {
            # File type importance
            'file_types': {
                'security': 10,  # Security files are very important
                'database': 8,   # Database files are very important
                'api': 7,        # API files are important
                'config': 6,     # Config files are important
                'core': 8,       # Core functionality is important
                'test': 3,       # Tests are less important
                'documentation': 2,  # Documentation is less important
            },
            # Change type importance
            'change_types': {
                'security': 10,  # Security changes are very important
                'bugfix': 8,     # Bug fixes are important
                'feature': 7,    # Features are important
                'refactor': 5,   # Refactoring is medium importance
                'performance': 6,  # Performance changes are medium-high importance
            },
            # File extension importance
            'file_extensions': {
                '.py': 5,  # Python files are medium importance
                '.js': 5,  # JavaScript files are medium importance
                '.java': 5,  # Java files are medium importance
                '.cpp': 6,  # C++ files are medium-high importance
                '.c': 6,    # C files are medium-high importance
                '.h': 5,    # Header files are medium importance
                '.sql': 8,  # SQL files are high importance
                '.html': 3,  # HTML files are low importance
                '.css': 3,  # CSS files are low importance
                '.json': 4,  # JSON files are low-medium importance
                '.xml': 4,  # XML files are low-medium importance
                '.yaml': 4,  # YAML files are low-medium importance
                '.yml': 4,  # YAML files are low-medium importance
                '.md': 2,  # Markdown files are low importance
                '.txt': 2,  # Text files are low importance
            }
        }
        
        # File type patterns
        self.file_type_patterns = {
            'security': r'(auth|security|encrypt|password|token)',
            'database': r'(db|database|sql|migration|schema)',
            'api': r'(api|endpoint|controller|route)',
            'config': r'(config|conf|settings|\.env|\.ini|\.yaml|\.yml|\.json|\.xml)',
            'core': r'(core|main|app|server|service)',
            'test': r'(test|spec|_test|_spec)',
            'documentation': r'(doc|readme|guide|manual|tutorial)',
        }
        
        # Change type patterns
        self.change_type_patterns = {
            'security': r'(security|vulnerability|exploit|attack)',
            'bugfix': r'(fix|bug|issue|error|exception)',
            'feature': r'(feature|add|implement|create|new)',
            'refactor': r'(refactor|restructure|reorganize|cleanup)',
            'performance': r'(performance|optimize|speed|fast)',
        }
        
    def pre_commit(self, repo: Repo, changed_files: List[str]) -> None:
        """Analyze the changed files and prioritize them for review."""
        if not changed_files:
            return
            
        # Prioritize files
        prioritized_files = self._prioritize_files(changed_files)
        
        # Store the prioritized files
        self.prioritized_files = prioritized_files
        
    def post_commit(self, repo: Repo, commit: Commit) -> None:
        """Add the file prioritization to the commit message."""
        if not hasattr(self, 'prioritized_files'):
            return
            
        # Get the current commit message
        message = commit.message
        
        # Add the file prioritization to the message
        priority_message = "\n\nFile Prioritization for Review:"
        
        # Group files by priority level
        priority_groups = {
            "High Priority": [],
            "Medium Priority": [],
            "Low Priority": []
        }
        
        for file_path, priority in self.prioritized_files:
            if priority >= 7:
                priority_groups["High Priority"].append(file_path)
            elif priority >= 4:
                priority_groups["Medium Priority"].append(file_path)
            else:
                priority_groups["Low Priority"].append(file_path)
        
        # Add files to the message
        for priority_level, files in priority_groups.items():
            if files:
                priority_message += f"\n\n{priority_level}:"
                for file_path in files:
                    priority_message += f"\n- {file_path}"
        
        # Update the commit message
        new_message = message + priority_message
        repo.git.commit('--amend', '-m', new_message, '--no-edit')
        
        print(f"Added file prioritization to commit message")
        
    def _prioritize_files(self, changed_files: List[str]) -> List[Tuple[str, int]]:
        """Prioritize files for review based on their importance and the types of changes made."""
        prioritized_files = []
        
        for file_path in changed_files:
            # Calculate file importance
            importance = self._calculate_file_importance(file_path)
            
            # Add to prioritized files
            prioritized_files.append((file_path, importance))
        
        # Sort by importance (descending)
        prioritized_files.sort(key=lambda x: x[1], reverse=True)
        
        return prioritized_files
    
    def _calculate_file_importance(self, file_path: str) -> int:
        """Calculate the importance of a file based on its type and the changes made."""
        importance = 0
        
        # Check file type
        for file_type, pattern in self.file_type_patterns.items():
            if re.search(pattern, file_path, re.IGNORECASE):
                if file_type in self.importance_factors['file_types']:
                    importance += self.importance_factors['file_types'][file_type]
        
        # Check change type
        for change_type, pattern in self.change_type_patterns.items():
            if re.search(pattern, file_path, re.IGNORECASE):
                if change_type in self.importance_factors['change_types']:
                    importance += self.importance_factors['change_types'][change_type]
        
        # Check file extension
        ext = os.path.splitext(file_path)[1].lower()
        if ext in self.importance_factors['file_extensions']:
            importance += self.importance_factors['file_extensions'][ext]
        
        # Normalize importance to a scale of 1-10
        importance = min(max(importance, 1), 10)
        
        return importance 