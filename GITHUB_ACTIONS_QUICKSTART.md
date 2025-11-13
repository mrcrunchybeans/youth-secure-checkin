# Quick Setup: GitHub Actions Auto-Build

## 1️⃣ Get Docker Hub Token (2 minutes)

1. Go to: https://hub.docker.com/settings/security
2. Click **New Access Token**
3. Description: `GitHub Actions`
4. Permissions: **Read, Write, Delete**
5. Click **Generate**
6. **Copy the token** (starts with `dckr_pat_`)

## 2️⃣ Add Secrets to GitHub (2 minutes)

1. Go to: https://github.com/mrcrunchybeans/youth-secure-checkin/settings/secrets/actions
2. Click **New repository secret**

### Secret 1:
```
Name: DOCKER_HUB_USERNAME
Value: mrcrunchybeans
```
Click **Add secret**

### Secret 2:
```
Name: DOCKER_HUB_TOKEN
Value: [paste token from step 1]
```
Click **Add secret**

## 3️⃣ Push Workflow File (30 seconds)

```powershell
git add .github/workflows/docker-publish.yml
git commit -m "Add GitHub Actions workflow for Docker auto-build"
git push
```

## 4️⃣ Watch It Build! (3-5 minutes)

Go to: https://github.com/mrcrunchybeans/youth-secure-checkin/actions

You'll see the workflow running. That's it! 🎉

---

## What Happens Now?

✅ Every push to master → New Docker image built automatically
✅ Every release → Tagged Docker image (v1.0.0, v1.1.0, etc.)
✅ Always get `latest` tag updated

## Manual Trigger (Optional)

1. Go to: https://github.com/mrcrunchybeans/youth-secure-checkin/actions
2. Click **Build and Push Docker Image**
3. Click **Run workflow** → **Run workflow**

---

**Need detailed help?** See `GITHUB_ACTIONS_SETUP.md`
