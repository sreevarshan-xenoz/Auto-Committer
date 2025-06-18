import os
import re
import tempfile
import webbrowser
from typing import List, Dict, Optional
from git import Repo, Commit
from .base import BasePlugin

class DiffViewerPlugin(BasePlugin):
    """Plugin that provides a visual representation of changes in the commit."""
    
    name = "DiffViewer"
    
    def __init__(self, config=None):
        super().__init__(config)
        self.temp_dir = tempfile.mkdtemp(prefix="auto_committer_diff_")
        self.html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Diff Viewer - {commit_id}</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            border-bottom: 1px solid #eee;
            padding-bottom: 10px;
        }
        .commit-info {
            margin-bottom: 20px;
            padding: 10px;
            background-color: #f9f9f9;
            border-radius: 3px;
        }
        .file-diff {
            margin-bottom: 30px;
            border: 1px solid #ddd;
            border-radius: 3px;
        }
        .file-header {
            padding: 10px;
            background-color: #f0f0f0;
            border-bottom: 1px solid #ddd;
            font-weight: bold;
        }
        .diff-content {
            font-family: monospace;
            white-space: pre;
            overflow-x: auto;
            padding: 10px;
        }
        .line {
            padding: 2px 5px;
        }
        .line-number {
            color: #999;
            user-select: none;
            padding-right: 10px;
            text-align: right;
            display: inline-block;
            width: 40px;
        }
        .addition {
            background-color: #e6ffed;
        }
        .deletion {
            background-color: #ffeef0;
        }
        .addition .line-number {
            color: #22863a;
        }
        .deletion .line-number {
            color: #cb2431;
        }
        .addition .line-content {
            color: #22863a;
        }
        .deletion .line-content {
            color: #cb2431;
        }
        .line-content {
            display: inline-block;
        }
        .summary {
            margin-top: 20px;
            padding: 10px;
            background-color: #f9f9f9;
            border-radius: 3px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Diff Viewer</h1>
        
        <div class="commit-info">
            <p><strong>Commit ID:</strong> {commit_id}</p>
            <p><strong>Author:</strong> {author}</p>
            <p><strong>Date:</strong> {date}</p>
            <p><strong>Message:</strong> {message}</p>
        </div>
        
        <div class="summary">
            <p><strong>Summary:</strong> {summary}</p>
        </div>
        
        {diff_content}
    </div>
</body>
</html>
"""
        
    def pre_commit(self, repo: Repo, changed_files: List[str]) -> None:
        """Store the changed files for later use."""
        self.changed_files = changed_files
        
    def post_commit(self, repo: Repo, commit: Commit) -> None:
        """Generate a visual representation of the changes."""
        if not hasattr(self, 'changed_files') or not self.changed_files:
            return
            
        try:
            # Get the diff
            diff = repo.git.diff('HEAD~1', 'HEAD')
            
            # Generate HTML
            html_content = self._generate_html(repo, commit, diff)
            
            # Save to file
            html_file = os.path.join(self.temp_dir, f"diff_{commit.hexsha[:8]}.html")
            with open(html_file, 'w') as f:
                f.write(html_content)
            
            # Open in browser
            webbrowser.open(f"file://{html_file}")
            
            print(f"Diff viewer opened in browser: {html_file}")
            
        except Exception as e:
            print(f"Failed to generate diff viewer: {e}")
    
    def _generate_html(self, repo: Repo, commit: Commit, diff: str) -> str:
        """Generate HTML content for the diff viewer."""
        # Parse the diff
        diff_sections = self._parse_diff(diff)
        
        # Generate diff content HTML
        diff_content_html = ""
        for file_path, lines in diff_sections.items():
            diff_content_html += f"""
            <div class="file-diff">
                <div class="file-header">{file_path}</div>
                <div class="diff-content">
"""
            
            for line in lines:
                line_type = line['type']
                line_number = line['line_number']
                content = line['content']
                
                if line_type == 'addition':
                    diff_content_html += f'<div class="line addition"><span class="line-number">+{line_number}</span><span class="line-content">{content}</span></div>\n'
                elif line_type == 'deletion':
                    diff_content_html += f'<div class="line deletion"><span class="line-number">-{line_number}</span><span class="line-content">{content}</span></div>\n'
                else:
                    diff_content_html += f'<div class="line"><span class="line-number">{line_number}</span><span class="line-content">{content}</span></div>\n'
            
            diff_content_html += """
                </div>
            </div>
"""
        
        # Generate summary
        summary = self._generate_summary(diff_sections)
        
        # Fill in the template
        html = self.html_template.format(
            commit_id=commit.hexsha[:8],
            author=f"{commit.author.name} <{commit.author.email}>",
            date=commit.committed_datetime.strftime("%Y-%m-%d %H:%M:%S"),
            message=commit.message,
            summary=summary,
            diff_content=diff_content_html
        )
        
        return html
    
    def _parse_diff(self, diff: str) -> Dict[str, List[Dict]]:
        """Parse the diff into sections by file."""
        sections = {}
        current_file = None
        current_lines = []
        
        for line in diff.split('\n'):
            # Check for file header
            if line.startswith('diff --git'):
                if current_file and current_lines:
                    sections[current_file] = current_lines
                
                # Extract file path
                match = re.search(r'diff --git a/(.+) b/(.+)', line)
                if match:
                    current_file = match.group(2)
                    current_lines = []
            
            # Check for line content
            elif line.startswith('+') and not line.startswith('+++'):
                current_lines.append({
                    'type': 'addition',
                    'line_number': len([l for l in current_lines if l['type'] != 'deletion']) + 1,
                    'content': line[1:]
                })
            elif line.startswith('-') and not line.startswith('---'):
                current_lines.append({
                    'type': 'deletion',
                    'line_number': len([l for l in current_lines if l['type'] != 'addition']) + 1,
                    'content': line[1:]
                })
            elif line.startswith(' ') and current_file:
                current_lines.append({
                    'type': 'context',
                    'line_number': len([l for l in current_lines if l['type'] != 'deletion']) + 1,
                    'content': line[1:]
                })
        
        # Add the last section
        if current_file and current_lines:
            sections[current_file] = current_lines
        
        return sections
    
    def _generate_summary(self, diff_sections: Dict[str, List[Dict]]) -> str:
        """Generate a summary of the changes."""
        total_files = len(diff_sections)
        total_additions = sum(len([l for l in lines if l['type'] == 'addition']) for lines in diff_sections.values())
        total_deletions = sum(len([l for l in lines if l['type'] == 'deletion']) for lines in diff_sections.values())
        
        return f"Changed {total_files} files with {total_additions} additions and {total_deletions} deletions." 