import os
import re
import tempfile
import webbrowser
from typing import List, Dict, Optional
from git import Repo, Commit
from .base import BasePlugin

class GitVisualizerPlugin(BasePlugin):
    """Plugin that generates a visual representation of the Git commit history."""
    
    name = "GitVisualizer"
    
    def __init__(self, config=None):
        super().__init__(config)
        self.temp_dir = tempfile.mkdtemp(prefix="auto_committer_git_visualizer_")
        self.html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Git Commit History Visualization</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
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
        .chart-container {
            margin-top: 20px;
            margin-bottom: 20px;
        }
        .commit-list {
            margin-top: 20px;
        }
        .commit-item {
            padding: 10px;
            border-bottom: 1px solid #eee;
        }
        .commit-item:hover {
            background-color: #f9f9f9;
        }
        .commit-id {
            font-family: monospace;
            color: #0366d6;
        }
        .commit-author {
            color: #666;
        }
        .commit-date {
            color: #999;
            font-size: 0.9em;
        }
        .commit-message {
            margin-top: 5px;
        }
        .stats {
            display: flex;
            flex-wrap: wrap;
            margin-top: 20px;
        }
        .stat-item {
            flex: 1;
            min-width: 200px;
            padding: 10px;
            margin: 5px;
            background-color: #f9f9f9;
            border-radius: 3px;
            text-align: center;
        }
        .stat-value {
            font-size: 1.5em;
            font-weight: bold;
            color: #0366d6;
        }
        .stat-label {
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Git Commit History Visualization</h1>
        
        <div class="stats">
            <div class="stat-item">
                <div class="stat-value">{total_commits}</div>
                <div class="stat-label">Total Commits</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{total_authors}</div>
                <div class="stat-label">Authors</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{first_commit_date}</div>
                <div class="stat-label">First Commit</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{last_commit_date}</div>
                <div class="stat-label">Last Commit</div>
            </div>
        </div>
        
        <div class="chart-container">
            <canvas id="commitsOverTime"></canvas>
        </div>
        
        <div class="chart-container">
            <canvas id="commitsByAuthor"></canvas>
        </div>
        
        <div class="chart-container">
            <canvas id="commitsByDay"></canvas>
        </div>
        
        <h2>Recent Commits</h2>
        <div class="commit-list">
            {commit_list}
        </div>
    </div>
    
    <script>
        // Commits over time chart
        const commitsOverTimeCtx = document.getElementById('commitsOverTime').getContext('2d');
        new Chart(commitsOverTimeCtx, {
            type: 'line',
            data: {
                labels: {commit_dates},
                datasets: [{
                    label: 'Commits',
                    data: {commit_counts},
                    borderColor: '#0366d6',
                    backgroundColor: 'rgba(3, 102, 214, 0.1)',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Commits Over Time'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0
                        }
                    }
                }
            }
        });
        
        // Commits by author chart
        const commitsByAuthorCtx = document.getElementById('commitsByAuthor').getContext('2d');
        new Chart(commitsByAuthorCtx, {
            type: 'pie',
            data: {
                labels: {author_names},
                datasets: [{
                    data: {author_counts},
                    backgroundColor: [
                        '#0366d6',
                        '#28a745',
                        '#ffc107',
                        '#dc3545',
                        '#17a2b8',
                        '#6c757d',
                        '#fd7e14',
                        '#20c997',
                        '#e83e8c',
                        '#6f42c1'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Commits by Author'
                    }
                }
            }
        });
        
        // Commits by day chart
        const commitsByDayCtx = document.getElementById('commitsByDay').getContext('2d');
        new Chart(commitsByDayCtx, {
            type: 'bar',
            data: {
                labels: {day_names},
                datasets: [{
                    label: 'Commits',
                    data: {day_counts},
                    backgroundColor: '#0366d6'
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Commits by Day of Week'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0
                        }
                    }
                }
            }
        });
    </script>
</body>
</html>
"""
        
    def post_commit(self, repo: Repo, commit: Commit) -> None:
        """Generate a visual representation of the Git commit history."""
        try:
            # Get commit history
            commits = list(repo.iter_commits())
            
            # Generate HTML
            html_content = self._generate_html(repo, commits)
            
            # Save to file
            html_file = os.path.join(self.temp_dir, "git_visualizer.html")
            with open(html_file, 'w') as f:
                f.write(html_content)
            
            # Open in browser
            webbrowser.open(f"file://{html_file}")
            
            print(f"Git visualizer opened in browser: {html_file}")
            
        except Exception as e:
            print(f"Failed to generate Git visualizer: {e}")
    
    def _generate_html(self, repo: Repo, commits: List[Commit]) -> str:
        """Generate HTML content for the Git visualizer."""
        # Get commit data
        commit_data = self._get_commit_data(commits)
        
        # Generate commit list HTML
        commit_list_html = ""
        for commit in commits[:20]:  # Show only the 20 most recent commits
            commit_list_html += f"""
            <div class="commit-item">
                <div>
                    <span class="commit-id">{commit.hexsha[:8]}</span>
                    <span class="commit-author">{commit.author.name}</span>
                    <span class="commit-date">{commit.committed_datetime.strftime("%Y-%m-%d %H:%M:%S")}</span>
                </div>
                <div class="commit-message">{commit.message.split('\\n')[0]}</div>
            </div>
            """
        
        # Fill in the template
        html = self.html_template.format(
            total_commits=len(commits),
            total_authors=len(commit_data['authors']),
            first_commit_date=commit_data['first_commit_date'],
            last_commit_date=commit_data['last_commit_date'],
            commit_dates=commit_data['commit_dates'],
            commit_counts=commit_data['commit_counts'],
            author_names=commit_data['author_names'],
            author_counts=commit_data['author_counts'],
            day_names=commit_data['day_names'],
            day_counts=commit_data['day_counts'],
            commit_list=commit_list_html
        )
        
        return html
    
    def _get_commit_data(self, commits: List[Commit]) -> Dict:
        """Get data for the Git visualizer."""
        # Initialize data
        commit_data = {
            'authors': {},
            'dates': {},
            'days': {
                'Monday': 0,
                'Tuesday': 0,
                'Wednesday': 0,
                'Thursday': 0,
                'Friday': 0,
                'Saturday': 0,
                'Sunday': 0
            },
            'first_commit_date': '',
            'last_commit_date': ''
        }
        
        # Process commits
        for commit in commits:
            # Get author
            author = commit.author.name
            if author in commit_data['authors']:
                commit_data['authors'][author] += 1
            else:
                commit_data['authors'][author] = 1
            
            # Get date
            date = commit.committed_datetime.strftime("%Y-%m-%d")
            if date in commit_data['dates']:
                commit_data['dates'][date] += 1
            else:
                commit_data['dates'][date] = 1
            
            # Get day of week
            day = commit.committed_datetime.strftime("%A")
            commit_data['days'][day] += 1
        
        # Sort dates
        sorted_dates = sorted(commit_data['dates'].keys())
        
        # Get first and last commit dates
        if sorted_dates:
            commit_data['first_commit_date'] = sorted_dates[0]
            commit_data['last_commit_date'] = sorted_dates[-1]
        
        # Prepare data for charts
        commit_data['commit_dates'] = sorted_dates
        commit_data['commit_counts'] = [commit_data['dates'][date] for date in sorted_dates]
        
        # Sort authors by commit count
        sorted_authors = sorted(commit_data['authors'].items(), key=lambda x: x[1], reverse=True)
        commit_data['author_names'] = [author for author, _ in sorted_authors]
        commit_data['author_counts'] = [count for _, count in sorted_authors]
        
        # Sort days
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        commit_data['day_names'] = day_order
        commit_data['day_counts'] = [commit_data['days'][day] for day in day_order]
        
        return commit_data 