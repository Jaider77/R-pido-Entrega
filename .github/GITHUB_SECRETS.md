# 🔐 GitHub Secrets Configuration

## Required Secrets for CI/CD Pipelines

### Docker Registry

- `DOCKER_USERNAME`: Your Docker Hub username
- `DOCKER_PASSWORD`: Your Docker Hub personal access token

### Notifications

- `SLACK_WEBHOOK`: Slack webhook URL for notifications

### Code Quality

- `SONAR_TOKEN`: SonarCloud API token
- `CODECOV_TOKEN`: Codecov API token (optional, auto-detected)

### Deployment

- `STAGING_DEPLOY_KEY`: SSH private key for staging server
- `PRODUCTION_DEPLOY_KEY`: SSH private key for production server

## How to Set Up

1. Go to your GitHub repository
2. Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Add each secret with its value

## Naming Convention

All secrets should be uppercase with underscores:

- ✅ `DOCKER_USERNAME`
- ❌ `docker_username` (incorrect)

## Security Best Practices

1. **Never commit secrets** to the repository
2. **Rotate tokens** regularly (every 90 days)
3. **Use organization secrets** for shared credentials
4. **Enable secret scanning** in GitHub settings
5. **Audit secret access** through GitHub logs
