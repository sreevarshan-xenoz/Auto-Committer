import os
import json
import requests
from typing import List, Dict, Optional
from git import Repo, Commit
from .base import BasePlugin

class MobileIntegrationPlugin(BasePlugin):
    """Plugin that sends notifications to mobile devices."""
    
    name = "MobileIntegration"
    
    def __init__(self, config=None):
        super().__init__(config)
        # Load configuration
        self.config = config or {}
        
        # Get API key from environment or config
        self.api_key = os.environ.get('PUSHOVER_API_KEY') or self.config.get('pushover_api_key')
        
        # Get user key from environment or config
        self.user_key = os.environ.get('PUSHOVER_USER_KEY') or self.config.get('pushover_user_key')
        
        # Get device name from environment or config
        self.device = os.environ.get('PUSHOVER_DEVICE') or self.config.get('pushover_device')
        
        # Check if API key and user key are set
        if not self.api_key or not self.user_key:
            print("Warning: Pushover API key or user key not set. Mobile notifications will be disabled.")
        
    def post_commit(self, repo: Repo, commit: Commit) -> None:
        """Send a notification to mobile devices after a commit."""
        if not self.api_key or not self.user_key:
            return
            
        try:
            # Get commit details
            commit_id = commit.hexsha[:8]
            author = f"{commit.author.name} <{commit.author.email}>"
            date = commit.committed_datetime.strftime("%Y-%m-%d %H:%M:%S")
            message = commit.message
            
            # Create notification message
            title = f"New Commit: {commit_id}"
            body = f"Author: {author}\nDate: {date}\n\n{message}"
            
            # Send notification
            self._send_notification(title, body)
            
            print(f"Sent mobile notification for commit {commit_id}")
            
        except Exception as e:
            print(f"Failed to send mobile notification: {e}")
    
    def on_push(self, repo: Repo, commit: Commit) -> None:
        """Send a notification to mobile devices after a push."""
        if not self.api_key or not self.user_key:
            return
            
        try:
            # Get commit details
            commit_id = commit.hexsha[:8]
            author = f"{commit.author.name} <{commit.author.email}>"
            date = commit.committed_datetime.strftime("%Y-%m-%d %H:%M:%S")
            message = commit.message
            
            # Get remote details
            remote = repo.remote()
            remote_name = remote.name
            remote_url = remote.url
            
            # Create notification message
            title = f"Code Pushed: {commit_id}"
            body = f"Author: {author}\nDate: {date}\nRemote: {remote_name} ({remote_url})\n\n{message}"
            
            # Send notification
            self._send_notification(title, body)
            
            print(f"Sent mobile notification for push of commit {commit_id}")
            
        except Exception as e:
            print(f"Failed to send mobile notification: {e}")
    
    def on_error(self, error: Exception) -> None:
        """Send a notification to mobile devices when an error occurs."""
        if not self.api_key or not self.user_key:
            return
            
        try:
            # Create notification message
            title = "Auto-Committer Error"
            body = f"An error occurred in the auto-committer:\n\n{str(error)}"
            
            # Send notification
            self._send_notification(title, body, priority=1)  # High priority
            
            print(f"Sent mobile notification for error: {error}")
            
        except Exception as e:
            print(f"Failed to send mobile notification: {e}")
    
    def _send_notification(self, title: str, body: str, priority: int = 0) -> None:
        """Send a notification to mobile devices using Pushover."""
        # Prepare data
        data = {
            'token': self.api_key,
            'user': self.user_key,
            'title': title,
            'message': body,
            'priority': priority
        }
        
        # Add device if specified
        if self.device:
            data['device'] = self.device
        
        # Send request
        response = requests.post('https://api.pushover.net/1/messages.json', data=data)
        
        # Check response
        if response.status_code != 200:
            print(f"Failed to send notification: {response.text}") 