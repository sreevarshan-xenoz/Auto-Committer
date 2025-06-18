import os
import re
import json
from typing import List, Dict, Optional
from git import Repo, Commit
from .base import BasePlugin

class CommitKarmaPlugin(BasePlugin):
    """Plugin that rewards good commit practices with a karma system."""
    
    name = "CommitKarma"
    
    def __init__(self, config=None):
        super().__init__(config)
        # Define karma rules
        self.karma_rules = {
            # Commit message rules
            'message': {
                'descriptive': 5,  # Descriptive commit message
                'follows_convention': 3,  # Follows commit convention
                'references_issue': 2,  # References an issue
                'too_short': -2,  # Too short commit message
                'too_long': -1,  # Too long commit message
            },
            # File rules
            'files': {
                'includes_tests': 3,  # Includes tests
                'includes_docs': 2,  # Includes documentation
                'too_many_files': -2,  # Too many files in one commit
                'large_file': -3,  # Large file
            },
            # Code rules
            'code': {
                'no_todos': 2,  # No TODOs in code
                'no_commented_code': 2,  # No commented code
                'no_debug_code': 3,  # No debug code
                'no_console_logs': 2,  # No console logs
            }
        }
        
        # Commit message patterns
        self.message_patterns = {
            'descriptive': r'^[A-Z][a-z]+(?:\([a-z]+\))?: .{10,}',  # Descriptive commit message
            'follows_convention': r'^(feat|fix|docs|style|refactor|test|chore)(?:\([a-z]+\))?: ',  # Follows convention
            'references_issue': r'(?:#|issue|ticket)\d+',  # References an issue
            'too_short': r'^.{0,10}$',  # Too short
            'too_long': r'^.{100,}$',  # Too long
        }
        
        # File patterns
        self.file_patterns = {
            'includes_tests': r'(test|spec|_test|_spec)',
            'includes_docs': r'(doc|readme|guide|manual|tutorial)',
        }
        
        # Code patterns
        self.code_patterns = {
            'no_todos': r'(TODO|FIXME|XXX|HACK)',
            'no_commented_code': r'//.*\{.*\}',  # Commented code blocks
            'no_debug_code': r'(debug|console\.log|print|alert)',  # Debug code
            'no_console_logs': r'console\.log',  # Console logs
        }
        
        # Karma file path
        self.karma_file = os.path.join(os.path.expanduser('~'), '.auto_committer_karma.json')
        
        # Load karma data
        self.karma_data = self._load_karma_data()
        
    def pre_commit(self, repo: Repo, changed_files: List[str]) -> None:
        """Store the changed files for later use."""
        self.changed_files = changed_files
        
    def post_commit(self, repo: Repo, commit: Commit) -> None:
        """Calculate karma for the commit and update the karma data."""
        if not hasattr(self, 'changed_files'):
            return
            
        # Calculate karma
        karma = self._calculate_karma(repo, commit)
        
        # Update karma data
        self._update_karma_data(karma)
        
        # Add karma to commit message
        self._add_karma_to_commit_message(repo, commit, karma)
        
    def _calculate_karma(self, repo: Repo, commit: Commit) -> Dict:
        """Calculate karma for the commit."""
        karma = {
            'total': 0,
            'message': 0,
            'files': 0,
            'code': 0,
            'details': {}
        }
        
        # Check commit message
        message = commit.message
        karma['details']['message'] = {}
        
        for rule, points in self.karma_rules['message'].items():
            if re.search(self.message_patterns[rule], message, re.IGNORECASE):
                karma['message'] += points
                karma['details']['message'][rule] = points
        
        # Check files
        karma['details']['files'] = {}
        
        # Check if includes tests
        if any(re.search(self.file_patterns['includes_tests'], f, re.IGNORECASE) for f in self.changed_files):
            karma['files'] += self.karma_rules['files']['includes_tests']
            karma['details']['files']['includes_tests'] = self.karma_rules['files']['includes_tests']
        
        # Check if includes docs
        if any(re.search(self.file_patterns['includes_docs'], f, re.IGNORECASE) for f in self.changed_files):
            karma['files'] += self.karma_rules['files']['includes_docs']
            karma['details']['files']['includes_docs'] = self.karma_rules['files']['includes_docs']
        
        # Check if too many files
        if len(self.changed_files) > 10:
            karma['files'] += self.karma_rules['files']['too_many_files']
            karma['details']['files']['too_many_files'] = self.karma_rules['files']['too_many_files']
        
        # Check code
        karma['details']['code'] = {}
        
        for file_path in self.changed_files:
            try:
                # Skip non-text files
                if not self._is_text_file(file_path):
                    continue
                    
                # Get file content
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Check for TODOs
                if not re.search(self.code_patterns['no_todos'], content, re.IGNORECASE):
                    karma['code'] += self.karma_rules['code']['no_todos']
                    karma['details']['code']['no_todos'] = self.karma_rules['code']['no_todos']
                
                # Check for commented code
                if not re.search(self.code_patterns['no_commented_code'], content, re.IGNORECASE):
                    karma['code'] += self.karma_rules['code']['no_commented_code']
                    karma['details']['code']['no_commented_code'] = self.karma_rules['code']['no_commented_code']
                
                # Check for debug code
                if not re.search(self.code_patterns['no_debug_code'], content, re.IGNORECASE):
                    karma['code'] += self.karma_rules['code']['no_debug_code']
                    karma['details']['code']['no_debug_code'] = self.karma_rules['code']['no_debug_code']
                
                # Check for console logs
                if not re.search(self.code_patterns['no_console_logs'], content, re.IGNORECASE):
                    karma['code'] += self.karma_rules['code']['no_console_logs']
                    karma['details']['code']['no_console_logs'] = self.karma_rules['code']['no_console_logs']
                
            except Exception:
                # Skip files that can't be read
                continue
        
        # Calculate total karma
        karma['total'] = karma['message'] + karma['files'] + karma['code']
        
        return karma
    
    def _update_karma_data(self, karma: Dict) -> None:
        """Update the karma data with the new karma."""
        # Add commit karma
        self.karma_data['commits'].append({
            'date': karma.get('date', ''),
            'message': karma.get('message', ''),
            'karma': karma['total']
        })
        
        # Update total karma
        self.karma_data['total_karma'] += karma['total']
        
        # Update karma level
        self.karma_data['karma_level'] = self._get_karma_level(self.karma_data['total_karma'])
        
        # Save karma data
        self._save_karma_data()
    
    def _add_karma_to_commit_message(self, repo: Repo, commit: Commit, karma: Dict) -> None:
        """Add karma to the commit message."""
        # Get the current commit message
        message = commit.message
        
        # Add karma to the message
        karma_message = f"\n\nCommit Karma: {karma['total']} points"
        
        if karma['details']:
            karma_message += "\nKarma Details:"
            
            if karma['details'].get('message'):
                karma_message += "\n- Message:"
                for rule, points in karma['details']['message'].items():
                    karma_message += f"\n  - {rule}: {points} points"
            
            if karma['details'].get('files'):
                karma_message += "\n- Files:"
                for rule, points in karma['details']['files'].items():
                    karma_message += f"\n  - {rule}: {points} points"
            
            if karma['details'].get('code'):
                karma_message += "\n- Code:"
                for rule, points in karma['details']['code'].items():
                    karma_message += f"\n  - {rule}: {points} points"
        
        # Add total karma
        karma_message += f"\n\nTotal Karma: {self.karma_data['total_karma']} points"
        karma_message += f"\nKarma Level: {self.karma_data['karma_level']}"
        
        # Update the commit message
        new_message = message + karma_message
        repo.git.commit('--amend', '-m', new_message, '--no-edit')
        
        print(f"Added commit karma to commit message: {karma['total']} points")
    
    def _load_karma_data(self) -> Dict:
        """Load karma data from file."""
        if os.path.exists(self.karma_file):
            try:
                with open(self.karma_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        
        # Default karma data
        return {
            'total_karma': 0,
            'karma_level': 'Novice',
            'commits': []
        }
    
    def _save_karma_data(self) -> None:
        """Save karma data to file."""
        try:
            with open(self.karma_file, 'w') as f:
                json.dump(self.karma_data, f, indent=2)
        except Exception as e:
            print(f"Failed to save karma data: {e}")
    
    def _get_karma_level(self, karma: int) -> str:
        """Get karma level based on total karma."""
        if karma < 10:
            return "Novice"
        elif karma < 50:
            return "Apprentice"
        elif karma < 100:
            return "Journeyman"
        elif karma < 200:
            return "Master"
        elif karma < 500:
            return "Grandmaster"
        else:
            return "Legend"
    
    def _is_text_file(self, file_path: str) -> bool:
        """Check if a file is a text file."""
        # Skip binary files
        binary_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico', '.pdf', '.zip', '.tar', '.gz', '.rar', '.7z', '.exe', '.dll', '.so', '.dylib']
        
        ext = os.path.splitext(file_path)[1].lower()
        if ext in binary_extensions:
            return False
        
        # Try to read the file as text
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                f.read(1024)
            return True
        except Exception:
            return False 