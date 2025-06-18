class BasePlugin:
    """Base class for all plugins."""
    name = "BasePlugin"
    def __init__(self, config=None):
        self.config = config or {}

    def pre_commit(self, repo, changed_files):
        """Hook to run before a commit. Can modify commit message or files."""
        pass

    def post_commit(self, repo, commit):
        """Hook to run after a commit is created."""
        pass

    def on_push(self, repo, commit):
        """Hook to run after a push to remote."""
        pass

    def on_error(self, error):
        """Hook to handle errors in the commit process."""
        pass 