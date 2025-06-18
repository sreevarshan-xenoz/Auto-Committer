import re
from typing import List, Dict, Optional
from git import Repo, Commit
from .base import BasePlugin

class IntentionAwarePlugin(BasePlugin):
    """Plugin that analyzes developer intentions from commit messages."""
    
    name = "IntentionAware"
    
    def __init__(self, config=None):
        super().__init__(config)
        # Define intention patterns
        self.intention_patterns = {
            # Feature intentions
            'feature': {
                'patterns': [
                    r'add\s+.*feature',
                    r'implement\s+.*feature',
                    r'create\s+.*feature',
                    r'new\s+.*feature',
                    r'add\s+.*functionality',
                    r'implement\s+.*functionality',
                    r'create\s+.*functionality',
                    r'new\s+.*functionality',
                    r'add\s+.*capability',
                    r'implement\s+.*capability',
                    r'create\s+.*capability',
                    r'new\s+.*capability',
                ],
                'description': 'Adding new features or functionality'
            },
            # Bug fix intentions
            'bugfix': {
                'patterns': [
                    r'fix\s+.*bug',
                    r'fix\s+.*issue',
                    r'fix\s+.*error',
                    r'fix\s+.*exception',
                    r'fix\s+.*problem',
                    r'fix\s+.*crash',
                    r'fix\s+.*failure',
                    r'fix\s+.*defect',
                    r'fix\s+.*flaw',
                    r'fix\s+.*vulnerability',
                    r'fix\s+.*security',
                    r'fix\s+.*leak',
                ],
                'description': 'Fixing bugs or issues'
            },
            # Refactoring intentions
            'refactor': {
                'patterns': [
                    r'refactor',
                    r'restructure',
                    r'reorganize',
                    r'cleanup',
                    r'clean\s+up',
                    r'improve\s+.*code',
                    r'enhance\s+.*code',
                    r'optimize\s+.*code',
                    r'better\s+.*code',
                    r'better\s+.*structure',
                    r'better\s+.*organization',
                    r'better\s+.*design',
                ],
                'description': 'Refactoring or improving code'
            },
            # Performance intentions
            'performance': {
                'patterns': [
                    r'performance',
                    r'optimize',
                    r'speed\s+up',
                    r'faster',
                    r'efficient',
                    r'efficiency',
                    r'optimization',
                    r'improve\s+.*performance',
                    r'enhance\s+.*performance',
                    r'better\s+.*performance',
                    r'reduce\s+.*time',
                    r'reduce\s+.*memory',
                    r'reduce\s+.*space',
                ],
                'description': 'Improving performance or efficiency'
            },
            # Security intentions
            'security': {
                'patterns': [
                    r'security',
                    r'vulnerability',
                    r'exploit',
                    r'attack',
                    r'secure',
                    r'protection',
                    r'protect',
                    r'defense',
                    r'defend',
                    r'safe',
                    r'safety',
                    r'secure\s+.*data',
                    r'protect\s+.*data',
                    r'secure\s+.*user',
                    r'protect\s+.*user',
                ],
                'description': 'Improving security or fixing vulnerabilities'
            },
            # Documentation intentions
            'documentation': {
                'patterns': [
                    r'documentation',
                    r'document',
                    r'readme',
                    r'guide',
                    r'manual',
                    r'tutorial',
                    r'comment',
                    r'explain',
                    r'clarify',
                    r'clarification',
                    r'description',
                    r'describe',
                    r'detail',
                    r'details',
                ],
                'description': 'Improving documentation or adding comments'
            },
            # Testing intentions
            'testing': {
                'patterns': [
                    r'test',
                    r'testing',
                    r'unit\s+test',
                    r'integration\s+test',
                    r'functional\s+test',
                    r'regression\s+test',
                    r'coverage',
                    r'coverage\s+test',
                    r'coverage\s+report',
                    r'coverage\s+analysis',
                    r'coverage\s+improvement',
                    r'coverage\s+enhancement',
                ],
                'description': 'Adding or improving tests'
            },
            # Dependency intentions
            'dependency': {
                'patterns': [
                    r'dependency',
                    r'dependencies',
                    r'package',
                    r'packages',
                    r'library',
                    r'libraries',
                    r'framework',
                    r'frameworks',
                    r'update\s+.*dependency',
                    r'update\s+.*package',
                    r'update\s+.*library',
                    r'update\s+.*framework',
                    r'upgrade\s+.*dependency',
                    r'upgrade\s+.*package',
                    r'upgrade\s+.*library',
                    r'upgrade\s+.*framework',
                ],
                'description': 'Updating or managing dependencies'
            },
            # Configuration intentions
            'configuration': {
                'patterns': [
                    r'config',
                    r'configuration',
                    r'settings',
                    r'setting',
                    r'environment',
                    r'environments',
                    r'env',
                    r'envs',
                    r'config\s+.*file',
                    r'config\s+.*files',
                    r'config\s+.*setting',
                    r'config\s+.*settings',
                ],
                'description': 'Updating or managing configuration'
            },
            # Deployment intentions
            'deployment': {
                'patterns': [
                    r'deploy',
                    r'deployment',
                    r'release',
                    r'releases',
                    r'version',
                    r'versions',
                    r'build',
                    r'builds',
                    r'ci',
                    r'cd',
                    r'continuous\s+integration',
                    r'continuous\s+deployment',
                    r'continuous\s+delivery',
                ],
                'description': 'Deploying or releasing code'
            }
        }
        
    def pre_commit(self, repo: Repo, changed_files: List[str]) -> None:
        """Store the changed files for later use."""
        self.changed_files = changed_files
        
    def post_commit(self, repo: Repo, commit: Commit) -> None:
        """Analyze the developer's intentions from the commit message."""
        if not hasattr(self, 'changed_files'):
            return
            
        try:
            # Get commit message
            message = commit.message
            
            # Analyze intentions
            intentions = self._analyze_intentions(message)
            
            # Add intentions to commit message
            self._add_intentions_to_commit_message(repo, commit, intentions)
            
        except Exception as e:
            print(f"Failed to analyze intentions: {e}")
    
    def _analyze_intentions(self, message: str) -> Dict:
        """Analyze the developer's intentions from the commit message."""
        intentions = {}
        
        # Check for intentions
        for intention, data in self.intention_patterns.items():
            for pattern in data['patterns']:
                if re.search(pattern, message, re.IGNORECASE):
                    intentions[intention] = {
                        'description': data['description'],
                        'confidence': self._calculate_confidence(message, pattern)
                    }
                    break
        
        return intentions
    
    def _calculate_confidence(self, message: str, pattern: str) -> float:
        """Calculate the confidence level of an intention match."""
        # Simple confidence calculation based on pattern match
        # This could be improved with more sophisticated NLP techniques
        
        # Check if the pattern is at the beginning of the message
        if re.match(pattern, message, re.IGNORECASE):
            return 1.0
        
        # Check if the pattern is in the first line of the message
        first_line = message.split('\n')[0]
        if re.search(pattern, first_line, re.IGNORECASE):
            return 0.9
        
        # Check if the pattern is in the message
        if re.search(pattern, message, re.IGNORECASE):
            return 0.7
        
        return 0.0
    
    def _add_intentions_to_commit_message(self, repo: Repo, commit: Commit, intentions: Dict) -> None:
        """Add the analyzed intentions to the commit message."""
        if not intentions:
            return
            
        # Get the current commit message
        message = commit.message
        
        # Add intentions to the message
        intention_message = "\n\nDeveloper Intentions:"
        
        for intention, data in intentions.items():
            confidence = data['confidence']
            description = data['description']
            
            # Format confidence as percentage
            confidence_percent = int(confidence * 100)
            
            intention_message += f"\n- {intention.capitalize()} ({confidence_percent}%): {description}"
        
        # Update the commit message
        new_message = message + intention_message
        repo.git.commit('--amend', '-m', new_message, '--no-edit')
        
        print(f"Added developer intentions to commit message") 