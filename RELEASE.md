# Release & Deployment Automation

## Semantic Versioning
- Managed by bump2version.
- To bump version: `bump2version patch|minor|major`
- Tags and commits are created automatically.

## Changelog Automation
- Managed by auto-changelog.
- To update changelog: `auto-changelog -p`

## Deployment
- Run `./deploy.sh` for POC deployment steps.
- For MVP, upgrade to full CI/CD deployment in GitHub Actions.

## Next Steps
- Add more deployment logic to `deploy.sh` as needed.
- Integrate release and deploy steps into CI for automated releases.
