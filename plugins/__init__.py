from .base import BasePlugin
from .smart_commit_message import SmartCommitMessagePlugin
from .code_quality_notes import CodeQualityNotesPlugin
from .diff_viewer import DiffViewerPlugin
from .bug_risk_score import BugRiskScorePlugin
from .file_prioritization import FilePrioritizationPlugin
from .commit_karma import CommitKarmaPlugin
from .mobile_integration import MobileIntegrationPlugin
from .git_visualizer import GitVisualizerPlugin
from .intention_aware import IntentionAwarePlugin
from .branch_management import BranchManagementPlugin

# List of all available plugins
available_plugins = {
    'smart_commit_message': SmartCommitMessagePlugin,
    'code_quality_notes': CodeQualityNotesPlugin,
    'diff_viewer': DiffViewerPlugin,
    'bug_risk_score': BugRiskScorePlugin,
    'file_prioritization': FilePrioritizationPlugin,
    'commit_karma': CommitKarmaPlugin,
    'mobile_integration': MobileIntegrationPlugin,
    'git_visualizer': GitVisualizerPlugin,
    'intention_aware': IntentionAwarePlugin,
    'branch_management': BranchManagementPlugin,
}

def get_plugin(name, config=None):
    """Get a plugin by name."""
    if name in available_plugins:
        return available_plugins[name](config)
    return None

def get_available_plugins():
    """Get a list of all available plugins."""
    return list(available_plugins.keys()) 