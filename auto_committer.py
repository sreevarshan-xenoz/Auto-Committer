import os
import time
import logging
import yaml
import re
import hashlib
from datetime import datetime, time as dt_time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv
from git import Repo, GitCommandError
import schedule
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class AutoCommitterError(Exception):
    """Custom exception for auto-committer specific errors"""
    pass

class SecurityScanner:
    """Scans files for potential security violations before committing"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.secret_patterns = [
            re.compile(pattern, re.IGNORECASE) 
            for pattern in config.get('secret_patterns', [])
        ]
        self.blocked_extensions = config.get('blocked_extensions', [])
        
    def scan_for_secrets(self, file_paths: List[str]) -> List[Dict]:
        """Scan files for potential secrets and return violations"""
        violations = []
        
        for file_path in file_paths:
            try:
                # Check file extension
                if any(file_path.endswith(ext) for ext in self.blocked_extensions):
                    violations.append({
                        'file': file_path,
                        'type': 'blocked_extension',
                        'severity': 'high'
                    })
                    continue
                
                # Skip binary files
                if self._is_binary_file(file_path):
                    continue
                    
                # Scan file content
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                for pattern in self.secret_patterns:
                    matches = pattern.findall(content)
                    for match in matches:
                        violations.append({
                            'file': file_path,
                            'type': 'potential_secret',
                            'pattern': pattern.pattern,
                            'match': match[:50] + '...' if len(match) > 50 else match,
                            'severity': 'medium'
                        })
                        
            except Exception as e:
                logging.warning(f"Could not scan {file_path}: {e}")
        
        return violations
    
    def _is_binary_file(self, file_path: str) -> bool:
        """Check if file is binary"""
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                return b'\0' in chunk
        except:
            return True
    
    def is_safe_to_commit(self, file_paths: List[str]) -> Tuple[bool, List[Dict]]:
        """Determine if it's safe to commit the given files"""
        violations = self.scan_for_secrets(file_paths)
        high_severity = [v for v in violations if v['severity'] == 'high']
        return len(high_severity) == 0, violations

class CommitMessageGenerator:
    """Generates intelligent commit messages using templates or AI"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.ai_enabled = config.get('enabled', False)
        
        if self.ai_enabled:
            try:
                from openai import OpenAI
                api_key = os.getenv("OPENAI_API_KEY")
                if api_key:
                    self.client = OpenAI(api_key=api_key)
                else:
                    logging.warning("OpenAI API key not found, disabling AI features")
                    self.ai_enabled = False
            except ImportError:
                logging.warning("OpenAI library not installed, disabling AI features")
                self.ai_enabled = False
    
    def generate_commit_message(self, changed_files: List[str], diff_content: str = "") -> str:
        """Generate appropriate commit message"""
        if self.ai_enabled and diff_content:
            ai_message = self._generate_ai_message(diff_content)
            if ai_message:
                return ai_message
        
        return self._generate_template_message(changed_files)
    
    def _generate_ai_message(self, diff_content: str) -> Optional[str]:
        """Generate commit message using AI"""
        prompt = f"""
        Summarize the following git diff into a single, concise commit message 
        following conventional commit guidelines (type: subject). 
        Focus on the main purpose of the changes.
        
        Diff:
        {diff_content[:2000]}
        
        Generate only the commit message, no explanation.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.get('model', 'gpt-3.5-turbo'),
                messages=[
                    {"role": "system", "content": "You are a developer who writes excellent commit messages."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.3
            )
            
            message = response.choices[0].message.content.strip()
            return message.strip('"\'')  # Remove quotes if present
            
        except Exception as e:
            logging.error(f"AI commit message generation failed: {e}")
            return None
    
    def _generate_template_message(self, changed_files: List[str]) -> str:
        """Generate template-based commit message"""
        file_count = len(changed_files)
        
        if file_count == 1:
            return f"auto: update {Path(changed_files[0]).name}"
        else:
            return f"auto: update {file_count} files 🚀"

class ChangeHandler(FileSystemEventHandler):
    """Handles file system events for real-time monitoring"""
    
    def __init__(self, callback, config: Dict):
        self.callback = callback
        self.debounce_time = config.get('debounce_seconds', 5)
        self.ignore_patterns = config.get('ignore_patterns', [])
        self.last_trigger = {}
        
    def should_ignore(self, file_path: str) -> bool:
        """Check if file should be ignored based on patterns"""
        for pattern in self.ignore_patterns:
            if pattern.replace('*', '') in file_path:
                return True
        return False
    
    def on_modified(self, event):
        if not event.is_directory and not self.should_ignore(event.src_path):
            self._handle_change(event.src_path)
    
    def on_created(self, event):
        if not event.is_directory and not self.should_ignore(event.src_path):
            self._handle_change(event.src_path)
    
    def _handle_change(self, file_path: str):
        """Handle file change with debouncing"""
        current_time = time.time()
        
        if file_path in self.last_trigger:
            if current_time - self.last_trigger[file_path] < self.debounce_time:
                return
        
        self.last_trigger[file_path] = current_time
        logging.info(f"File change detected: {file_path}")
        
        # Trigger commit after small delay to ensure file is stable
        time.sleep(1)
        self.callback()

class EnhancedAutoCommitter:
    """Main auto-committer class with comprehensive functionality"""
    
    def __init__(self, config_path: str = 'auto_committer_config.yaml'):
        """Initialize the auto-committer with configuration"""
        load_dotenv()
        self.config = self._load_config(config_path)
        self._setup_logging()
        self._initialize_components()
        
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logging.error(f"Config file not found: {config_path}")
            raise AutoCommitterError(f"Configuration file {config_path} not found")
        except yaml.YAMLError as e:
            logging.error(f"Error parsing config: {e}")
            raise AutoCommitterError(f"Invalid configuration file: {e}")
    
    def _setup_logging(self):
        """Setup comprehensive logging"""
        log_config = self.config.get('logging', {})
        
        logging.basicConfig(
            level=getattr(logging, log_config.get('level', 'INFO')),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_config.get('file_path', 'auto_committer.log')),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _initialize_components(self):
        """Initialize all system components"""
        repo_path = self.config['repository']['path']
        
        # Validate repository
        if not os.path.isdir(repo_path):
            raise AutoCommitterError(f"Repository path does not exist: {repo_path}")
        
        try:
            self.repo = Repo(repo_path)
            if self.repo.bare:
                raise AutoCommitterError("Cannot work with bare repositories")
        except Exception as e:
            raise AutoCommitterError(f"Failed to initialize repository: {e}")
        
        # Initialize components
        self.security_scanner = SecurityScanner(self.config.get('security', {}))
        self.message_generator = CommitMessageGenerator(self.config.get('ai_integration', {}))
        
        # Setup file monitoring if enabled
        self.observer = None
        if self.config.get('file_monitoring', {}).get('enabled', False):
            self._setup_file_monitoring()
        
        self.running = False
    
    def _setup_file_monitoring(self):
        """Setup real-time file monitoring"""
        handler = ChangeHandler(self.attempt_commit, self.config['file_monitoring'])
        self.observer = Observer()
        self.observer.schedule(
            handler, 
            self.config['repository']['path'], 
            recursive=True
        )
    
    def _is_quiet_hours(self) -> bool:
        """Check if current time is within configured quiet hours"""
        quiet_config = self.config.get('scheduling', {}).get('quiet_hours')
        if not quiet_config:
            return False
        
        try:
            quiet_start = dt_time.fromisoformat(quiet_config['start'])
            quiet_end = dt_time.fromisoformat(quiet_config['end'])
            current_time = datetime.now().time()
            
            if quiet_start <= quiet_end:
                return quiet_start <= current_time <= quiet_end
            else:  # Spans midnight
                return current_time >= quiet_start or current_time <= quiet_end
        except:
            return False
    
    def _get_changed_files(self) -> List[str]:
        """Get list of changed files in repository"""
        changed_files = []
        
        # Get modified tracked files
        for item in self.repo.index.diff(None):
            changed_files.append(item.a_path)
        
        # Get untracked files
        changed_files.extend(self.repo.untracked_files)
        
        return changed_files
    
    def _should_commit(self, changed_files: List[str]) -> bool:
        """Determine if commit should proceed based on policies"""
        commit_config = self.config.get('commit_behavior', {})
        
        # Check quiet hours
        if self._is_quiet_hours():
            self.logger.info("Skipping commit during quiet hours")
            return False
        
        # Check file count thresholds
        file_count = len(changed_files)
        min_files = commit_config.get('min_files_for_commit', 1)
        max_files = commit_config.get('max_files_per_commit', 50)
        
        if file_count < min_files:
            self.logger.info(f"Not enough files changed ({file_count} < {min_files})")
            return False
        
        if file_count > max_files:
            self.logger.warning(f"Too many files changed ({file_count} > {max_files})")
            return False
        
        return True
    
    def attempt_commit(self) -> bool:
        """Attempt to create and push a commit"""
        try:
            # Check for changes
            if not self.repo.is_dirty(untracked_files=True):
                self.logger.info("No changes detected")
                return False
            
            # Get changed files
            changed_files = self._get_changed_files()
            
            # Check commit policies
            if not self._should_commit(changed_files):
                return False
            
            # Security scan
            if self.config.get('security', {}).get('scan_for_secrets', True):
                is_safe, violations = self.security_scanner.is_safe_to_commit(changed_files)
                
                if not is_safe:
                    self.logger.error(f"Security violations detected: {len(violations)}")
                    for violation in violations:
                        self.logger.error(f"  {violation['file']}: {violation['type']}")
                    return False
                
                if violations:
                    self.logger.warning(f"Security warnings: {len(violations)}")
                    for violation in violations:
                        self.logger.warning(f"  {violation['file']}: {violation['type']}")
            
            # Stage all changes
            self.repo.git.add(all=True)
            self.logger.info(f"Staged {len(changed_files)} files")
            
            # Generate commit message
            try:
                diff_content = self.repo.git.diff('--staged', '--stat')
                commit_message = self.message_generator.generate_commit_message(changed_files, diff_content)
            except:
                commit_message = f"auto: update {len(changed_files)} files 🚀"
            
            # Create commit
            commit = self.repo.index.commit(commit_message)
            self.logger.info(f"Created commit: {commit.hexsha[:8]} - {commit_message}")
            
            # Push to remote
            try:
                remote_name = self.config['repository'].get('remote', 'origin')
                branch_name = self.config['repository'].get('branch', 'main')
                
                # Attempt pull before push to minimize conflicts
                try:
                    origin = self.repo.remote(name=remote_name)
                    origin.pull(branch_name)
                    self.logger.info("Successfully pulled latest changes")
                except GitCommandError as e:
                    self.logger.warning(f"Pull failed, attempting push anyway: {e}")
                
                # Push changes
                origin.push(branch_name)
                self.logger.info("✅ Successfully pushed to remote")
                
                return True
                
            except GitCommandError as e:
                self.logger.error(f"Failed to push: {e}")
                self.logger.error("Manual intervention may be required")
                return False
            
        except Exception as e:
            self.logger.error(f"Commit attempt failed: {e}", exc_info=True)
            return False
    
    def start(self):
        """Start the auto-committer service"""
        self.logger.info("Starting Enhanced Auto-Committer")
        self.running = True
        
        # Start file monitoring if enabled
        if self.observer:
            self.observer.start()
            self.logger.info("File monitoring started")
        
        # Setup scheduling if enabled
        if self.config.get('scheduling', {}).get('enabled', True):
            interval = self.config['scheduling'].get('interval_minutes', 30)
            schedule.every(interval).minutes.do(self.attempt_commit)
            self.logger.info(f"Scheduled commits every {interval} minutes")
            
            # Run once immediately
            self.attempt_commit()
        
        try:
            while self.running:
                if not self.observer:  # Only run scheduler if not using file monitoring
                    schedule.run_pending()
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.logger.info("Shutting down auto-committer")
            self.stop()
    
    def stop(self):
        """Stop the auto-committer service"""
        self.running = False
        if self.observer:
            self.observer.stop()
            self.observer.join()
        self.logger.info("Auto-committer stopped")

# Main execution
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhanced Auto Git Committer")
    parser.add_argument('--config', default='auto_committer_config.yaml', 
                       help='Path to configuration file')
    parser.add_argument('--once', action='store_true', 
                       help='Run once and exit (useful for cron)')
    
    args = parser.parse_args()
    
    try:
        committer = EnhancedAutoCommitter(args.config)
        
        if args.once:
            success = committer.attempt_commit()
            exit(0 if success else 1)
        else:
            committer.start()
            
    except AutoCommitterError as e:
        print(f"Configuration Error: {e}")
        exit(1)
    except Exception as e:
        print(f"Unexpected Error: {e}")
        exit(1) 