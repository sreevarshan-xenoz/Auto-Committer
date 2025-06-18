# Enhanced Auto-Committer Installation Guide

This guide will help you set up and use the Enhanced Auto-Committer for your Git repositories.

## Prerequisites

- Python 3.8 or higher
- Git installed on your system
- A Git repository to monitor

## Installation Options

### Option 1: Direct Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/enhanced-auto-committer.git
   cd enhanced-auto-committer
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure the auto-committer:
   - Copy `.env.example` to `.env` and fill in your API keys and credentials
   - Edit `auto_committer_config.yaml` to match your repository settings

### Option 2: Using pip

```bash
pip install enhanced-auto-committer
```

### Option 3: Using Docker

1. Build the Docker image:
   ```bash
   docker build -t enhanced-auto-committer .
   ```

2. Run the container:
   ```bash
   docker run -v /path/to/your/repo:/app/repo enhanced-auto-committer
   ```

## Configuration

The main configuration file is `auto_committer_config.yaml`. Here are the key settings:

- `repository.path`: Path to your Git repository
- `repository.branch`: Branch to commit to
- `repository.remote`: Remote repository name
- `scheduling.enabled`: Enable scheduled commits
- `scheduling.interval_minutes`: Minutes between commits
- `file_monitoring.enabled`: Enable real-time file monitoring
- `security.scan_for_secrets`: Enable security scanning

## Usage

### Basic Usage

Run the auto-committer:

```bash
python auto_committer.py
```

### Run Once

To run once and exit (useful for cron jobs):

```bash
python auto_committer.py --once
```

### Using a Custom Config

```bash
python auto_committer.py --config /path/to/custom_config.yaml
```

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

### Using Docker Compose

Create a `docker-compose.yml` file:

```yaml
version: '3'
services:
  auto-committer:
    build: .
    volumes:
      - /path/to/your/repo:/app/repo
    environment:
      - OPENAI_API_KEY=your_api_key
    restart: always
```

Then run:

```bash
docker-compose up -d
```

## Troubleshooting

- Check the log file (`auto_committer.log`) for errors
- Ensure your Git repository is properly configured
- Verify that the repository path in the config is correct
- Make sure you have the necessary permissions to access the repository

## Advanced Features

### AI-Powered Commit Messages

To enable AI-powered commit messages:

1. Set `ai_integration.enabled: true` in the config
2. Add your OpenAI API key to the `.env` file

### Webhook Notifications

To enable webhook notifications:

1. Set `notifications.webhook.enabled: true` in the config
2. Add your webhook URL to the `.env` file

### Email Notifications

To enable email notifications:

1. Set `notifications.email.enabled: true` in the config
2. Add your email credentials to the `.env` file 