import re
from typing import List, Dict, Optional
from git import Repo, Commit
from .base import BasePlugin

class BranchManagementPlugin(BasePlugin):
    """Plugin that manages branch creation and merging."""
    
    name = "BranchManagement"
    
    def __init__(self, config=None):
        super().__init__(config)
        # Load configuration
        self.config = config or {}
        
        # Branch naming patterns
        self.branch_patterns = {
            'feature': r'feature/([a-z0-9-]+)',
            'bugfix': r'bugfix/([a-z0-9-]+)',
            'hotfix': r'hotfix/([a-z0-9-]+)',
            'release': r'release/([0-9]+\.[0-9]+\.[0-9]+)',
            'maintenance': r'maintenance/([a-z0-9-]+)',
        }
        
        # Branch protection rules
        self.branch_protection = {
            'main': {
                'require_review': True,
                'require_tests': True,
                'require_clean_build': True,
                'no_force_push': True,
                'no_direct_commits': True,
            },
            'develop': {
                'require_review': True,
                'require_tests': True,
                'require_clean_build': True,
                'no_force_push': True,
                'no_direct_commits': False,
            },
            'feature': {
                'require_review': False,
                'require_tests': True,
                'require_clean_build': False,
                'no_force_push': False,
                'no_direct_commits': False,
            },
            'bugfix': {
                'require_review': False,
                'require_tests': True,
                'require_clean_build': False,
                'no_force_push': False,
                'no_direct_commits': False,
            },
            'hotfix': {
                'require_review': True,
                'require_tests': True,
                'require_clean_build': True,
                'no_force_push': False,
                'no_direct_commits': False,
            },
            'release': {
                'require_review': True,
                'require_tests': True,
                'require_clean_build': True,
                'no_force_push': False,
                'no_direct_commits': False,
            },
            'maintenance': {
                'require_review': True,
                'require_tests': True,
                'require_clean_build': True,
                'no_force_push': False,
                'no_direct_commits': False,
            },
        }
        
    def pre_commit(self, repo: Repo, changed_files: List[str]) -> None:
        """Check if the commit is allowed on the current branch."""
        try:
            # Get current branch
            current_branch = repo.active_branch.name
            
            # Check branch protection rules
            self._check_branch_protection(repo, current_branch)
            
        except Exception as e:
            print(f"Failed to check branch protection: {e}")
    
    def post_commit(self, repo: Repo, commit: Commit) -> None:
        """Analyze the commit and suggest branch management actions."""
        try:
            # Get current branch
            current_branch = repo.active_branch.name
            
            # Analyze branch
            branch_type = self._get_branch_type(current_branch)
            
            # Get branch protection rules
            protection_rules = self._get_branch_protection_rules(branch_type)
            
            # Add branch management info to commit message
            self._add_branch_management_to_commit_message(repo, commit, current_branch, branch_type, protection_rules)
            
        except Exception as e:
            print(f"Failed to analyze branch: {e}")
    
    def on_push(self, repo: Repo, commit: Commit) -> None:
        """Check if the push is allowed and suggest branch management actions."""
        try:
            # Get current branch
            current_branch = repo.active_branch.name
            
            # Check if branch should be merged
            self._check_branch_merge(repo, current_branch)
            
        except Exception as e:
            print(f"Failed to check branch merge: {e}")
    
    def _check_branch_protection(self, repo: Repo, branch_name: str) -> None:
        """Check if the commit is allowed on the current branch."""
        # Get branch type
        branch_type = self._get_branch_type(branch_name)
        
        # Get branch protection rules
        protection_rules = self._get_branch_protection_rules(branch_type)
        
        # Check if direct commits are allowed
        if protection_rules.get('no_direct_commits', False):
            print(f"Warning: Direct commits are not allowed on {branch_name} branch.")
            print("Consider creating a feature branch and submitting a pull request.")
    
    def _check_branch_merge(self, repo: Repo, branch_name: str) -> None:
        """Check if the branch should be merged."""
        # Get branch type
        branch_type = self._get_branch_type(branch_name)
        
        # Check if branch should be merged
        if branch_type in ['feature', 'bugfix', 'hotfix']:
            print(f"Consider merging {branch_name} into develop or main branch.")
            
            # Check if branch is ready for merge
            if self._is_branch_ready_for_merge(repo, branch_name):
                print(f"{branch_name} is ready for merge.")
            else:
                print(f"{branch_name} is not ready for merge. Please ensure all tests pass and code review is completed.")
    
    def _get_branch_type(self, branch_name: str) -> str:
        """Get the type of branch based on its name."""
        for branch_type, pattern in self.branch_patterns.items():
            if re.match(pattern, branch_name):
                return branch_type
        
        # Default to 'other' if no pattern matches
        return 'other'
    
    def _get_branch_protection_rules(self, branch_type: str) -> Dict:
        """Get the protection rules for a branch type."""
        return self.branch_protection.get(branch_type, {})
    
    def _is_branch_ready_for_merge(self, repo: Repo, branch_name: str) -> bool:
        """Check if a branch is ready for merge."""
        # This is a simplified check. In a real implementation, you would:
        # 1. Check if all tests pass
        # 2. Check if code review is completed
        # 3. Check if there are no conflicts
        # 4. Check if the branch is up to date with the target branch
        
        # For now, we'll just return True
        return True
    
    def _add_branch_management_to_commit_message(self, repo: Repo, commit: Commit, branch_name: str, branch_type: str, protection_rules: Dict) -> None:
        """Add branch management information to the commit message."""
        # Get the current commit message
        message = commit.message
        
        # Add branch management info to the message
        branch_message = f"\n\nBranch Management:"
        branch_message += f"\n- Branch: {branch_name}"
        branch_message += f"\n- Type: {branch_type.capitalize()}"
        
        if protection_rules:
            branch_message += "\n- Protection Rules:"
            for rule, value in protection_rules.items():
                if value:
                    branch_message += f"\n  - {rule.replace('_', ' ').capitalize()}"
        
        # Update the commit message
        new_message = message + branch_message
        repo.git.commit('--amend', '-m', new_message, '--no-edit')
        
        print(f"Added branch management info to commit message") 