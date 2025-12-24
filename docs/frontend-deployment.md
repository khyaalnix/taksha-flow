# Frontend Deployment Guide

This guide explains how to deploy the frontend application to GitHub Pages using a tag-based versioning approach.

## Overview

The frontend is automatically deployed to **https://khyaalnix.github.io/flow** when you push a version tag. The deployment uses GitHub Actions and supports multiple release types.

## Supported Tag Formats

- **Production**: `v*.*.*` (e.g., `v1.0.0`, `v2.1.3`)
- **Beta**: `v*.*.*.beta.*` (e.g., `v1.0.0.beta.1`, `v1.2.0.beta.5`)
- **Alpha**: `v*.*.*.alpha.*` (e.g., `v1.0.0.alpha.1`)
- **Release Candidate**: `v*.*.*.rc.*` (e.g., `v1.0.0.rc.1`)

## Quick Deployment

### Using NPM Scripts (Recommended)

```bash
cd frontend

# Deploy beta version
npm run deploy:beta

# Deploy alpha version
npm run deploy:alpha

# Deploy release candidate
npm run deploy:rc

# Deploy production version
npm run deploy:prod
```

The script will:
1. Show you the current version and the new tag to be created
2. Ask for confirmation before proceeding
3. Create and push the tag automatically
4. Trigger the GitHub Actions workflow

### Manual Deployment

```bash
# 1. Create a tag
git tag -a v1.0.0.beta.1 -m "Release v1.0.0.beta.1"

# 2. Push the tag
git push origin v1.0.0.beta.1

# 3. GitHub Actions will automatically deploy
```

## Version Management

### Current Version

Check the current version in [frontend/package.json](frontend/package.json):

```bash
cd frontend
node -p "require('./package.json').version"
```

### Updating Version in package.json

```bash
cd frontend

# Bump patch version (0.1.0 -> 0.1.1)
npm version patch

# Bump minor version (0.1.0 -> 0.2.0)
npm version minor

# Bump major version (0.1.0 -> 1.0.0)
npm version major
```

## Deployment Workflow

### What Happens When You Push a Tag

1. **Validation**: Tag format is validated
2. **Build**:
   - Node.js environment setup
   - Dependencies installed
   - Linter runs
   - Next.js static export built
   - Version metadata created
3. **Deploy**:
   - Build artifacts uploaded to GitHub Pages
   - Site deployed to https://khyaalnix.github.io/flow
4. **Release** (for production and beta):
   - GitHub Release created
   - Changelog generated
   - Build artifacts attached

### Deployment Environment Variables

The following environment variables are automatically set during build:

- `GITHUB_PAGES=true` - Enables GitHub Pages mode
- `NODE_ENV=production` - Production build mode
- `NEXT_PUBLIC_VERSION` - The version number
- `NEXT_PUBLIC_BUILD_TIME` - Build timestamp

## Monitoring Deployments

### Check Workflow Status

Visit: https://github.com/khyaalnix/taksha-flow/actions

### Check Deployed Version

Once deployed, you can check the version info:
- **Version JSON**: https://khyaalnix.github.io/flow/version.json
- **Deployment Info**: https://khyaalnix.github.io/flow/DEPLOYMENT.txt

Example version.json:
```json
{
  "version": "1.0.0.beta.1",
  "tag": "v1.0.0.beta.1",
  "commit": "abc123def",
  "buildTime": "2025-01-15T10:30:00Z",
  "isProduction": false,
  "isBeta": true,
  "isAlpha": false,
  "isRC": false,
  "deployUrl": "https://khyaalnix.github.io/flow"
}
```

### View Recent Tags

```bash
# List all tags
git tag -l

# List tags matching pattern
git tag -l 'v1.0.*'

# List recent tags
git tag -l 'v*' | tail -10
```

## Rollback a Deployment

If you need to rollback to a previous version:

```bash
# 1. Find the previous tag
git tag -l 'v*' | tail -10

# 2. Push the old tag again (GitHub Pages will deploy it)
git push origin v1.0.0 --force
```

## Deleting Tags

If you created a tag by mistake:

```bash
# Delete local tag
git tag -d v1.0.0.beta.1

# Delete remote tag
git push --delete origin v1.0.0.beta.1
```

**Warning**: Deleting a tag that's already deployed won't un-deploy it. You'll need to push a new tag to update the deployment.

## Troubleshooting

### Tag Already Exists

```bash
# Error: Tag v1.0.0 already exists
git tag -d v1.0.0  # Delete local tag
git push --delete origin v1.0.0  # Delete remote tag
# Then create the tag again
```

### Build Fails

1. Check the [Actions tab](https://github.com/khyaalnix/taksha-flow/actions)
2. Review the build logs
3. Common issues:
   - Linting errors: Run `npm run lint` locally
   - Build errors: Run `npm run build:ghpages` locally
   - Missing dependencies: Run `npm ci`

### Deployment Not Updating

1. Check GitHub Actions workflow completed successfully
2. Wait a few minutes for GitHub Pages CDN to update
3. Try hard refresh in browser (Ctrl+Shift+R or Cmd+Shift+R)
4. Check Settings → Pages in GitHub repository settings

## Manual Trigger

You can also manually trigger a deployment from GitHub Actions UI:

1. Go to [Actions](https://github.com/khyaalnix/taksha-flow/actions)
2. Select "Deploy Frontend to GitHub Pages"
3. Click "Run workflow"
4. Enter the tag name (e.g., `v1.0.0.beta.1`)
5. Click "Run workflow"

## Release Types Explained

### Production (`v*.*.*`)
- For stable releases
- Creates a full GitHub Release
- Not marked as pre-release
- Use for production-ready code

### Beta (`v*.*.*.beta.*`)
- For beta testing
- Creates a GitHub Release marked as pre-release
- Use for feature-complete but not fully tested

### Alpha (`v*.*.*.alpha.*`)
- For early testing
- Does not create GitHub Release
- Use for experimental features

### Release Candidate (`v*.*.*.rc.*`)
- For final testing before production
- Does not create GitHub Release
- Use for near-production ready code

## Best Practices

1. **Always test locally** before deploying:
   ```bash
   cd frontend
   npm run build:ghpages
   ```

2. **Use semantic versioning**:
   - MAJOR: Breaking changes
   - MINOR: New features (backwards compatible)
   - PATCH: Bug fixes

3. **Use beta/alpha for testing**:
   - Test new features with beta tags first
   - Only use production tags for stable releases

4. **Keep commits clean**:
   - Ensure all changes are committed before creating tags
   - Use meaningful commit messages

5. **Document changes**:
   - Update CHANGELOG.md (if exists)
   - Use descriptive tag messages

## Examples

### Deploying a New Feature (Beta)

```bash
cd frontend
npm version minor  # 0.1.0 -> 0.2.0
npm run deploy:beta  # Creates v0.2.0.beta.1
```

### Deploying a Bug Fix (Production)

```bash
cd frontend
npm version patch  # 1.0.0 -> 1.0.1
npm run deploy:prod  # Creates v1.0.1
```

### Creating Multiple Beta Releases

```bash
npm run deploy:beta  # v1.0.0.beta.1
# Test, find bugs, fix them
npm run deploy:beta  # v1.0.0.beta.2
# Test again
npm run deploy:beta  # v1.0.0.beta.3
```

## GitHub Pages Configuration

Ensure the following settings in your GitHub repository:

1. Go to **Settings** → **Pages**
2. **Source**: GitHub Actions
3. Your site will be published at: https://khyaalnix.github.io/flow

## CI/CD Pipeline Summary

```
Push Tag → Validate → Install → Lint → Build → Test → Deploy → Release
```

- ⚡ **Fast**: Parallel jobs where possible
- 🔒 **Safe**: Validation and linting before deployment
- 📦 **Versioned**: Every deployment has version metadata
- 🚀 **Automated**: Zero manual steps after tag push

## Support

For issues or questions:
- Check [GitHub Actions logs](https://github.com/khyaalnix/taksha-flow/actions)
- Review [GitHub Pages documentation](https://docs.github.com/en/pages)
- Open an issue in the repository
