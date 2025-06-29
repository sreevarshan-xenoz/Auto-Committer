# Enhanced Auto-Committer

A sophisticated automation tool that streamlines Git workflows by intelligently detecting changes, staging files, generating meaningful commit messages, and pushing updates to remote repositories.

## Overview

The Enhanced Auto-Committer provides a robust, secure, and highly configurable solution for automating Git workflows while maintaining the flexibility to adapt to various development environments and requirements. The modular architecture ensures that you can start with basic functionality and progressively add advanced features as your needs evolve.

## Key Features

- **Real-time File Monitoring**: Automatically detects changes in your repository
- **Intelligent Commit Messages**: Generates contextual commit messages using templates or AI
- **Security Scanning**: Prevents accidental exposure of sensitive data
- **Configurable Scheduling**: Set up regular commits or quiet hours
- **Multiple Deployment Options**: Run as a service, in Docker, or directly
- **Comprehensive Logging**: Detailed logs for troubleshooting and monitoring

## Installation

### Using the Quick Start Script

#### On Windows:
```bash
quick_start.bat
```

#### On Unix-like systems:
```bash
chmod +x quick_start.sh
./quick_start.sh
```

### Manual Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/sreevarshan-xenoz/Auto-Committer.git
   cd Auto-Committer
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure the auto-committer:
   - Copy `.env.example` to `.env` and fill in your API keys and credentials
   - Edit `auto_committer_config.yaml` to match your repository settings

4. Run the auto-committer:
   ```bash
   python auto_committer.py
   ```

## Configuration

The main configuration file is `auto_committer_config.yaml`. Here are the key settings:

```yaml
repository:
  path: "."  # Path to your Git repository
  branch: "main"  # Branch to commit to
  remote: "origin"  # Remote repository name

scheduling:
  enabled: true  # Enable scheduled commits
  interval_minutes: 30  # Minutes between commits
  quiet_hours:  # Optional quiet hours
    start: "22:00"
    end: "08:00"

file_monitoring:
  enabled: false  # Enable real-time file monitoring
  debounce_seconds: 5  # Seconds to wait after a change before committing

security:
  scan_for_secrets: true  # Enable security scanning
  blocked_extensions:  # File extensions to block
    - ".env"
    - ".key" 
    - ".pem"
```

## Advanced Features

### AI-Powered Commit Messages

To enable AI-powered commit messages:

1. Set `ai_integration.enabled: true` in the config
2. Add your OpenAI API key to the `.env` file

### Notifications

Configure webhook or email notifications in the config file and `.env` file.

## Deployment

### As a System Service (Linux)

1. Edit the `auto-committer.service` file to match your environment
2. Copy it to the systemd directory:
   ```bash
   sudo cp auto-committer.service /etc/systemd/system/
   ```
3. Enable and start the service:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable auto-committer.service
   sudo systemctl start auto-committer.service
   ```

### Using Docker

```bash
docker build -t enhanced-auto-committer .
docker run -v /path/to/your/repo:/app/repo enhanced-auto-committer
```

Or using Docker Compose:

```bash
docker-compose up -d
```

## Troubleshooting

- Check the log file (`auto_committer.log`) for errors
- Ensure your Git repository is properly configured
- Verify that the repository path in the config is correct
- Make sure you have the necessary permissions to access the repository

## Security Considerations

The Enhanced Auto-Committer implements multiple security layers:

- **File-Based Security**: Blocks dangerous file extensions and detects potential secrets
- **Repository Safety**: Respects .gitignore rules and prevents excessive file changes
- **Conflict Detection**: Attempts to pull before pushing to minimize merge conflicts

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## Acknowledgements

This project was developed to address the need for a more robust and secure auto-committing solution for Git repositories.