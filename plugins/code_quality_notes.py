import re
import os
from typing import List, Dict, Optional
from git import Repo, Commit
from .base import BasePlugin

class CodeQualityNotesPlugin(BasePlugin):
    """Plugin that analyzes code changes and adds quality notes to commit messages."""
    
    name = "CodeQualityNotes"
    
    def __init__(self, config=None):
        super().__init__(config)
        self.quality_patterns = {
            'complexity': {
                'pattern': r'for\s+.*\s+for\s+.*\s+for\s+',  # Nested loops
                'message': 'High complexity detected (nested loops)'
            },
            'long_function': {
                'pattern': r'def\s+\w+\s*\([^)]*\)\s*:.*?(?=def|\Z)',
                'message': 'Long function detected'
            },
            'magic_numbers': {
                'pattern': r'\b\d{4,}\b',  # Numbers with 4+ digits
                'message': 'Magic number detected'
            },
            'hardcoded_strings': {
                'pattern': r'"[^"]{50,}"',  # Long strings
                'message': 'Long hardcoded string detected'
            },
            'commented_code': {
                'pattern': r'#\s*(if|for|while|def|class)\s+',  # Commented code
                'message': 'Commented code detected'
            },
            'todo': {
                'pattern': r'#\s*TODO|#\s*FIXME|#\s*XXX',  # TODO comments
                'message': 'TODO comment detected'
            }
        }
        
        # File extensions to analyze
        self.code_extensions = ['.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.c', '.cpp', '.go', '.rb', '.php']
        
    def pre_commit(self, repo: Repo, changed_files: List[str]) -> None:
        """Analyze changed files for code quality issues."""
        self.changed_files = changed_files
        self.quality_issues = self._analyze_code_quality(changed_files, repo)
        
    def post_commit(self, repo: Repo, commit: Commit) -> None:
        """Add code quality notes to the commit message."""
        if not hasattr(self, 'quality_issues') or not self.quality_issues:
            return
            
        # Get the original commit message
        original_message = commit.message
        
        # Create enhanced message with quality notes
        enhanced_message = self._add_quality_notes(original_message)
        
        # Only amend if the message has been enhanced
        if enhanced_message != original_message:
            try:
                # Amend the commit with the enhanced message
                repo.git.commit('--amend', '-m', enhanced_message, '--no-edit')
                print(f"Added code quality notes to commit message")
            except Exception as e:
                print(f"Failed to add code quality notes: {e}")
    
    def _analyze_code_quality(self, files: List[str], repo: Repo) -> Dict[str, List[Dict]]:
        """Analyze code quality in the changed files."""
        issues = {}
        
        for file_path in files:
            # Skip non-code files
            if not any(file_path.endswith(ext) for ext in self.code_extensions):
                continue
                
            try:
                # Get the file content
                if repo.is_dirty(path=file_path):
                    # File is modified but not committed yet
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                else:
                    # File is already committed
                    content = repo.git.show(f'HEAD:{file_path}')
                
                # Analyze the content
                file_issues = self._analyze_file_content(content, file_path)
                
                if file_issues:
                    issues[file_path] = file_issues
                    
            except Exception as e:
                print(f"Error analyzing {file_path}: {e}")
        
        return issues
    
    def _analyze_file_content(self, content: str, file_path: str) -> List[Dict]:
        """Analyze a file's content for code quality issues."""
        issues = []
        
        # Split content into lines for line number tracking
        lines = content.split('\n')
        
        for issue_type, issue_info in self.quality_patterns.items():
            pattern = issue_info['pattern']
            message = issue_info['message']
            
            # Find all matches
            for i, line in enumerate(lines):
                if re.search(pattern, line):
                    issues.append({
                        'type': issue_type,
                        'message': message,
                        'line': i + 1,
                        'line_content': line.strip()
                    })
        
        return issues
    
    def _add_quality_notes(self, original_message: str) -> str:
        """Add code quality notes to the commit message."""
        if not hasattr(self, 'quality_issues') or not self.quality_issues:
            return original_message
            
        # Don't enhance if the message already has detailed information
        if len(original_message.split('\n')) > 2:
            return original_message
            
        # Create enhanced message
        enhanced_message = original_message.rstrip()
        
        # Add quality notes
        enhanced_message += "\n\nCode Quality Notes:"
        
        # Group issues by type
        issue_types = {}
        for file_path, issues in self.quality_issues.items():
            for issue in issues:
                issue_type = issue['type']
                if issue_type not in issue_types:
                    issue_types[issue_type] = []
                issue_types[issue_type].append({
                    'file': file_path,
                    'line': issue['line'],
                    'message': issue['message']
                })
        
        # Add issues to the message
        for issue_type, issues in issue_types.items():
            enhanced_message += f"\n- {issue_type.title()}: {len(issues)} issues"
            for issue in issues[:3]:  # Limit to 3 examples per type
                enhanced_message += f"\n  - {issue['file']}:{issue['line']} - {issue['message']}"
            if len(issues) > 3:
                enhanced_message += f"\n  - ... and {len(issues) - 3} more"
        
        return enhanced_message 