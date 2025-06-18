import re
from typing import List, Dict, Optional
from git import Repo, Commit
from .base import BasePlugin

class BugRiskScorePlugin(BasePlugin):
    """Plugin that calculates a risk score for commits based on the types of changes made."""
    
    name = "BugRiskScore"
    
    def __init__(self, config=None):
        super().__init__(config)
        # Define risk factors and their weights
        self.risk_factors = {
            # File type risks
            'file_types': {
                'test': -0.2,  # Tests reduce risk
                'config': 0.3,  # Config changes increase risk
                'database': 0.4,  # Database changes are high risk
                'security': 0.5,  # Security changes are very high risk
                'api': 0.3,  # API changes are medium risk
                'ui': 0.2,  # UI changes are medium-low risk
                'documentation': -0.1,  # Documentation reduces risk
            },
            # Change type risks
            'change_types': {
                'refactor': 0.3,  # Refactoring is medium risk
                'bugfix': 0.2,  # Bug fixes are medium-low risk
                'feature': 0.4,  # Features are medium-high risk
                'performance': 0.3,  # Performance changes are medium risk
                'security': 0.5,  # Security changes are very high risk
            },
            # Code pattern risks
            'code_patterns': {
                'complexity': 0.3,  # Complex code is medium risk
                'magic_number': 0.2,  # Magic numbers are medium-low risk
                'hardcoded_string': 0.1,  # Hardcoded strings are low risk
                'commented_code': 0.1,  # Commented code is low risk
                'todo': 0.1,  # TODOs are low risk
            },
            # File extension risks
            'file_extensions': {
                '.py': 0.2,  # Python files are medium-low risk
                '.js': 0.2,  # JavaScript files are medium-low risk
                '.java': 0.2,  # Java files are medium-low risk
                '.cpp': 0.3,  # C++ files are medium risk
                '.c': 0.3,  # C files are medium risk
                '.h': 0.2,  # Header files are medium-low risk
                '.sql': 0.4,  # SQL files are medium-high risk
                '.html': 0.1,  # HTML files are low risk
                '.css': 0.1,  # CSS files are low risk
                '.json': 0.1,  # JSON files are low risk
                '.xml': 0.1,  # XML files are low risk
                '.yaml': 0.1,  # YAML files are low risk
                '.yml': 0.1,  # YAML files are low risk
                '.md': -0.1,  # Markdown files reduce risk
                '.txt': -0.1,  # Text files reduce risk
            }
        }
        
        # File type patterns
        self.file_type_patterns = {
            'test': r'(test|spec|_test|_spec)',
            'config': r'(config|conf|settings|\.env|\.ini|\.yaml|\.yml|\.json|\.xml)',
            'database': r'(db|database|sql|migration|schema)',
            'security': r'(auth|security|encrypt|password|token)',
            'api': r'(api|endpoint|controller|route)',
            'ui': r'(ui|view|template|component|css|html)',
            'documentation': r'(doc|readme|guide|manual|tutorial)',
        }
        
        # Change type patterns
        self.change_type_patterns = {
            'refactor': r'(refactor|restructure|reorganize|cleanup)',
            'bugfix': r'(fix|bug|issue|error|exception)',
            'feature': r'(feature|add|implement|create|new)',
            'performance': r'(performance|optimize|speed|fast)',
            'security': r'(security|vulnerability|exploit|attack)',
        }
        
        # Code pattern regexes
        self.code_pattern_regexes = {
            'complexity': re.compile(r'(if|for|while|switch).*\{.*\{.*\}.*\}'),  # Nested control structures
            'magic_number': re.compile(r'\b\d{3,}\b'),  # Numbers with 3+ digits
            'hardcoded_string': re.compile(r'"[^"]{20,}"'),  # Long strings
            'commented_code': re.compile(r'//.*\{.*\}'),  # Commented code blocks
            'todo': re.compile(r'(TODO|FIXME|XXX|HACK)'),  # TODO comments
        }
        
    def pre_commit(self, repo: Repo, changed_files: List[str]) -> None:
        """Analyze the changed files and calculate a risk score."""
        if not changed_files:
            return
            
        # Initialize risk score
        risk_score = 0.0
        risk_factors = []
        
        # Analyze file types
        file_types = self._analyze_file_types(changed_files)
        for file_type, count in file_types.items():
            if file_type in self.risk_factors['file_types']:
                risk_score += self.risk_factors['file_types'][file_type] * count
                risk_factors.append(f"{file_type}: {self.risk_factors['file_types'][file_type] * count:.2f}")
        
        # Analyze change types
        change_types = self._analyze_change_types(changed_files)
        for change_type, count in change_types.items():
            if change_type in self.risk_factors['change_types']:
                risk_score += self.risk_factors['change_types'][change_type] * count
                risk_factors.append(f"{change_type}: {self.risk_factors['change_types'][change_type] * count:.2f}")
        
        # Analyze file extensions
        file_extensions = self._analyze_file_extensions(changed_files)
        for ext, count in file_extensions.items():
            if ext in self.risk_factors['file_extensions']:
                risk_score += self.risk_factors['file_extensions'][ext] * count
                risk_factors.append(f"{ext}: {self.risk_factors['file_extensions'][ext] * count:.2f}")
        
        # Analyze code patterns
        code_patterns = self._analyze_code_patterns(repo, changed_files)
        for pattern, count in code_patterns.items():
            if pattern in self.risk_factors['code_patterns']:
                risk_score += self.risk_factors['code_patterns'][pattern] * count
                risk_factors.append(f"{pattern}: {self.risk_factors['code_patterns'][pattern] * count:.2f}")
        
        # Store the risk score and factors
        self.risk_score = risk_score
        self.risk_factors = risk_factors
        
    def post_commit(self, repo: Repo, commit: Commit) -> None:
        """Add the risk score to the commit message."""
        if not hasattr(self, 'risk_score'):
            return
            
        # Get the current commit message
        message = commit.message
        
        # Add the risk score to the message
        risk_level = self._get_risk_level(self.risk_score)
        risk_message = f"\n\nBug Risk Score: {self.risk_score:.2f} ({risk_level})"
        
        if self.risk_factors:
            risk_message += "\nRisk Factors:"
            for factor in self.risk_factors:
                risk_message += f"\n- {factor}"
        
        # Update the commit message
        new_message = message + risk_message
        repo.git.commit('--amend', '-m', new_message, '--no-edit')
        
        print(f"Added bug risk score to commit: {self.risk_score:.2f} ({risk_level})")
        
    def _analyze_file_types(self, changed_files: List[str]) -> Dict[str, int]:
        """Analyze the types of files changed."""
        file_types = {}
        
        for file_path in changed_files:
            for file_type, pattern in self.file_type_patterns.items():
                if re.search(pattern, file_path, re.IGNORECASE):
                    file_types[file_type] = file_types.get(file_type, 0) + 1
        
        return file_types
    
    def _analyze_change_types(self, changed_files: List[str]) -> Dict[str, int]:
        """Analyze the types of changes made."""
        change_types = {}
        
        for file_path in changed_files:
            for change_type, pattern in self.change_type_patterns.items():
                if re.search(pattern, file_path, re.IGNORECASE):
                    change_types[change_type] = change_types.get(change_type, 0) + 1
        
        return change_types
    
    def _analyze_file_extensions(self, changed_files: List[str]) -> Dict[str, int]:
        """Analyze the file extensions of changed files."""
        file_extensions = {}
        
        for file_path in changed_files:
            ext = os.path.splitext(file_path)[1].lower()
            if ext:
                file_extensions[ext] = file_extensions.get(ext, 0) + 1
        
        return file_extensions
    
    def _analyze_code_patterns(self, repo: Repo, changed_files: List[str]) -> Dict[str, int]:
        """Analyze the code patterns in changed files."""
        code_patterns = {}
        
        for file_path in changed_files:
            try:
                # Get the file content
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Check for code patterns
                for pattern_name, regex in self.code_pattern_regexes.items():
                    matches = regex.findall(content)
                    if matches:
                        code_patterns[pattern_name] = code_patterns.get(pattern_name, 0) + len(matches)
            except Exception:
                # Skip files that can't be read
                continue
        
        return code_patterns
    
    def _get_risk_level(self, risk_score: float) -> str:
        """Get a human-readable risk level based on the risk score."""
        if risk_score < 0:
            return "Very Low Risk"
        elif risk_score < 0.5:
            return "Low Risk"
        elif risk_score < 1.0:
            return "Medium Risk"
        elif risk_score < 2.0:
            return "High Risk"
        else:
            return "Very High Risk" 