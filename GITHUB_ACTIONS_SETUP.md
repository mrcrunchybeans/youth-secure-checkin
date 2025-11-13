# GitHub Actions Docker Auto-Build Setup

This guide will help you set up automatic Docker image building and publishing whenever you push code or create a release.

## 🎯 What This Does

When you push to GitHub or create a release:
1. GitHub Actions automatically builds your Docker image
2. Pushes it to Docker Hub as `mrcrunchybeans/youth-secure-checkin`
3. Tags it appropriately (latest, version numbers, etc.)
4. Updates the Docker Hub description

## 📋 Prerequisites

- Docker Hub account (mrcrunchybeans)
- GitHub repository (youth-secure-checkin)
- Admin access to both

## 🔑 Step 1: Create Docker Hub Access Token

1. Go to [Docker Hub](https://hub.docker.com)
2. Click your profile picture → **Account Settings**
3. Go to **Security** tab
4. Click **New Access Token**
5. Settings:
   - **Access Token Description**: `GitHub Actions - youth-secure-checkin`
   - **Access permissions**: `Read, Write, Delete`
6. Click **Generate**
7. **IMPORTANT:** Copy the token immediately (you won't see it again!)
   - It will look like: `dckr_pat_xxxxxxxxxxxxxxxxxxx`

## 🔐 Step 2: Add Secrets to GitHub

1. Go to your GitHub repository: https://github.com/mrcrunchybeans/youth-secure-checkin
2. Click **Settings** (top menu)
3. In left sidebar: **Secrets and variables** → **Actions**
4. Click **New repository secret**

### Add First Secret:
- **Name**: `DOCKER_HUB_USERNAME`
- **Value**: `mrcrunchybeans`
- Click **Add secret**

### Add Second Secret:
- **Name**: `DOCKER_HUB_TOKEN`
- **Value**: Paste the token you copied from Docker Hub
- Click **Add secret**

You should now see both secrets listed (values are hidden).

## ✅ Step 3: Verify Workflow File

The workflow file is already created at:
```
.github/workflows/docker-publish.yml
```

Commit and push it:
```powershell
git add .github/workflows/docker-publish.yml
git commit -m "Add GitHub Actions workflow for Docker auto-build"
git push
```

## 🚀 Step 4: Test the Workflow

### Option A: Push to Master (triggers build)
```powershell
# Make any change
git add .
git commit -m "Test auto-build"
git push
```

### Option B: Create a Release (recommended)
1. Go to: https://github.com/mrcrunchybeans/youth-secure-checkin/releases
2. Click **Draft a new release**
3. Click **Choose a tag** → Type `v1.0.0` → **Create new tag**
4. **Release title**: `v1.0.0 - Initial Public Release`
5. **Description**: Add release notes (see example below)
6. Click **Publish release**

**Example Release Notes:**
```markdown
## 🎉 Initial Public Release

### Features
- Secure family and kid check-in/check-out system
- QR code checkout and label printing support
- Customizable branding and organization settings
- Event management (iCal import or manual entry)
- Database utilities for maintenance
- Docker deployment ready

### Docker Image
Pull the image:
```bash
docker pull mrcrunchybeans/youth-secure-checkin:latest
docker pull mrcrunchybeans/youth-secure-checkin:1.0.0
```

See [DOCKER.md](DOCKER.md) for deployment instructions.

### Documentation
- [Quick Start Guide](README.md)
- [Docker Deployment](DOCKER.md)
- [Security Guide](SECURITY.md)
- [FAQ](docs/FAQ.md)
```

## 📊 Step 5: Monitor the Build

1. Go to **Actions** tab in your GitHub repository
2. You'll see the workflow running: "Build and Push Docker Image"
3. Click on it to see real-time logs
4. Build typically takes 3-5 minutes

### What Gets Built:

**On push to master branch:**
- `mrcrunchybeans/youth-secure-checkin:master`
- `mrcrunchybeans/youth-secure-checkin:latest`

**On release tag (e.g., v1.0.0):**
- `mrcrunchybeans/youth-secure-checkin:1.0.0`
- `mrcrunchybeans/youth-secure-checkin:1.0`
- `mrcrunchybeans/youth-secure-checkin:1`
- `mrcrunchybeans/youth-secure-checkin:latest`

## 🎯 How to Use After Setup

### For Regular Updates:
```powershell
# Make your changes
git add .
git commit -m "Add new feature"
git push
# Image automatically built and pushed to Docker Hub
```

### For New Versions:
```powershell
# Update version in code/docs if needed
git add .
git commit -m "Prepare v1.1.0 release"
git push

# Create release on GitHub (as shown in Step 4, Option B)
# Or use command line:
git tag -a v1.1.0 -m "Release v1.1.0"
git push origin v1.1.0
```

## 🔍 Troubleshooting

### Build fails with "authentication required"
**Solution:** Check that both secrets are added correctly:
- `DOCKER_HUB_USERNAME` = `mrcrunchybeans`
- `DOCKER_HUB_TOKEN` = Your access token

### Build fails with "permission denied"
**Solution:** Make sure your Docker Hub token has `Read, Write, Delete` permissions. Create a new token if needed.

### Workflow doesn't trigger
**Solution:** 
- Make sure `.github/workflows/docker-publish.yml` is committed and pushed
- Check that GitHub Actions is enabled: Settings → Actions → General → Allow all actions

### Image builds but doesn't appear on Docker Hub
**Solution:** Wait 1-2 minutes after build completes, then refresh Docker Hub page.

## 🎨 Customizing the Workflow

### Change when builds trigger:
Edit `.github/workflows/docker-publish.yml`, line 3-9:

```yaml
on:
  push:
    branches:
      - master      # Build on every push to master
  release:
    types: [published]  # Build on release
  workflow_dispatch:    # Allow manual trigger
```

### Add build notifications:
Add Slack/Discord/Email notifications by adding steps at the end of the workflow.

## 📚 Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Build Push Action](https://github.com/docker/build-push-action)
- [Docker Hub Documentation](https://docs.docker.com/docker-hub/)

## ✅ Verification Checklist

After setup, verify:

- [ ] Docker Hub access token created
- [ ] Both GitHub secrets added (`DOCKER_HUB_USERNAME` and `DOCKER_HUB_TOKEN`)
- [ ] Workflow file committed and pushed
- [ ] First build completed successfully
- [ ] Image appears on Docker Hub
- [ ] Can pull image: `docker pull mrcrunchybeans/youth-secure-checkin:latest`

---

## 🎉 Success!

Your Docker images will now build automatically whenever you:
- Push to master branch
- Create a new release
- Manually trigger the workflow

No more manual building and pushing! 🚀
