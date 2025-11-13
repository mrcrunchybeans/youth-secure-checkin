# Publishing to Docker Hub

This guide will walk you through publishing the Youth Secure Check-in Docker image to Docker Hub.

## Prerequisites

✅ Docker Desktop installed and running
✅ Docker Hub account (free tier is fine)
✅ Project tested locally with Docker

## Step 1: Create Docker Hub Account (if needed)

1. Go to https://hub.docker.com
2. Click "Sign Up"
3. Choose a username (this will be part of your image name)
4. Verify your email

## Step 2: Login to Docker Hub

```powershell
# Login to Docker Hub from command line
docker login

# Enter your Docker Hub username and password when prompted
```

You should see: `Login Succeeded`

## Step 3: Your Image Name

Your image will be: `mrcrunchybeans/youth-secure-checkin`

## Step 4: Build and Tag the Image

```powershell
# Build the image with latest tag
docker build -t mrcrunchybeans/youth-secure-checkin:latest .

# Build with multiple tags (latest + version number)
docker build -t mrcrunchybeans/youth-secure-checkin:latest -t mrcrunchybeans/youth-secure-checkin:1.0.0 .
```

**Build Arguments (optional):**
```powershell
# Build with multiple tags at once
docker build -t mrcrunchybeans/youth-secure-checkin:latest -t mrcrunchybeans/youth-secure-checkin:1.0.0 -t mrcrunchybeans/youth-secure-checkin:v1 .
```

## Step 5: Test the Tagged Image Locally

```powershell
# Stop any running containers
docker-compose down

# Test your tagged image (PowerShell syntax)
docker run -d -p 5000:5000 -e SECRET_KEY="test_secret_key_12345" -e DEVELOPER_PASSWORD="TestPass123" -v ${PWD}/data:/app/data -v ${PWD}/uploads:/app/uploads --name youth-checkin-test mrcrunchybeans/youth-secure-checkin:latest

# Check if it's running
docker ps

# Test in browser: http://localhost:5000

# Stop and remove test container
docker stop youth-checkin-test
docker rm youth-checkin-test
```

## Step 6: Push to Docker Hub

```powershell
# Push the latest tag
docker push mrcrunchybeans/youth-secure-checkin:latest

# Push version tag (if you created one)
docker push mrcrunchybeans/youth-secure-checkin:1.0.0

# Or push all tags at once
docker push mrcrunchybeans/youth-secure-checkin --all-tags
```

This will take a few minutes depending on your upload speed (image is ~200-300 MB).

## Step 7: Verify on Docker Hub

1. Go to https://hub.docker.com
2. Click on your profile → "Repositories"
3. You should see `youth-secure-checkin`
4. Click on it to see details and tags

## Step 8: Update Repository Description (Recommended)

On Docker Hub, add a description to help others:

**Short Description:**
```
Secure check-in/check-out system for youth organizations with QR codes, label printing, and family management.
```

**Full Description (README):**
```markdown
# Youth Secure Check-in

A secure, flexible check-in/check-out system for youth organizations including Trail Life, scouting groups, churches, schools, and community programs.

## Features

- Family and kid management
- Event tracking (iCal import or manual entry)
- QR code checkout or label printing
- Customizable branding
- Multi-level security
- Docker deployment ready

## Quick Start

1. Pull the image:
   ```bash
   docker pull mrcrunchybeans/youth-secure-checkin:latest
   ```

2. Create a `.env` file:
   ```bash
   SECRET_KEY=your_generated_secret_key_here
   DEVELOPER_PASSWORD=your_secure_password_here
   ```

3. Run with docker-compose:
   ```yaml
   services:
     web:
       image: mrcrunchybeans/youth-secure-checkin:latest
       ports:
         - "5000:5000"
       environment:
         - SECRET_KEY=${SECRET_KEY}
         - DEVELOPER_PASSWORD=${DEVELOPER_PASSWORD}
       volumes:
         - ./data:/app/data
         - ./uploads:/app/uploads
       restart: unless-stopped
   ```

4. Start: `docker-compose up -d`
5. Visit: http://localhost:5000

## Documentation

- GitHub: https://github.com/mrcrunchybeans/youth-secure-checkin
- Full Docker Guide: See DOCKER.md in repository
- Security Guide: See SECURITY.md in repository

## Support

For issues and questions, visit: https://github.com/mrcrunchybeans/youth-secure-checkin/issues

## License

MIT License - See LICENSE file in repository
```

## Step 9: Test Pull from Docker Hub

Test that others can pull your image:

```powershell
# Remove local image
docker rmi mrcrunchybeans/youth-secure-checkin:latest

# Pull from Docker Hub
docker pull mrcrunchybeans/youth-secure-checkin:latest

# Should download successfully
```

## Step 10: Update GitHub README

Add Docker Hub badge and pull instructions to your GitHub README.md:

```markdown
[![Docker Pulls](https://img.shields.io/docker/pulls/mrcrunchybeans/youth-secure-checkin)](https://hub.docker.com/r/mrcrunchybeans/youth-secure-checkin)
[![Docker Image Size](https://img.shields.io/docker/image-size/mrcrunchybeans/youth-secure-checkin/latest)](https://hub.docker.com/r/mrcrunchybeans/youth-secure-checkin)

## Docker Quick Start

Pull and run from Docker Hub:

\`\`\`bash
docker pull mrcrunchybeans/youth-secure-checkin:latest
docker-compose up -d
\`\`\`

See [DOCKER.md](DOCKER.md) for complete deployment guide.
```

## Updating the Image (Future Releases)

When you make changes and want to update Docker Hub:

```powershell
# 1. Update version number in your app or docs
# 2. Rebuild with new version tag
docker build -t mrcrunchybeans/youth-secure-checkin:latest -t mrcrunchybeans/youth-secure-checkin:1.0.1 .

# 3. Push both tags
docker push mrcrunchybeans/youth-secure-checkin:latest
docker push mrcrunchybeans/youth-secure-checkin:1.0.1

# 4. Update Docker Hub release notes
```

## Best Practices

### Version Tagging Strategy

- `latest` - Always points to most recent stable release
- `1.0.0` - Specific version (semantic versioning)
- `v1` - Major version tag
- `dev` - Development/testing builds (optional)

### Image Size Optimization

Current image size: ~200-300 MB (Python 3.11-slim base)

To check your image size:
```powershell
docker images mrcrunchybeans/youth-secure-checkin
```

### Security Scanning

Docker Hub automatically scans for vulnerabilities:
1. Go to your repository on Docker Hub
2. Click "Tags"
3. View security scan results

### Automated Builds (Optional)

Set up GitHub Actions to auto-build and push on release:

1. On Docker Hub, go to Account Settings → Security → New Access Token
2. Add token to GitHub Secrets as `DOCKER_HUB_TOKEN`
3. Create `.github/workflows/docker-publish.yml` (see repository for example)

## Troubleshooting

### "denied: requested access to the resource is denied"

**Solution:** Make sure you're logged in:
```powershell
docker login
docker tag youth-secure-checkin:latest mrcrunchybeans/youth-secure-checkin:latest
```

### "unauthorized: authentication required"

**Solution:** Login again:
```powershell
docker logout
docker login
```

### Push is very slow

**Solution:** Image size is normal (~200-300 MB). First push takes longest. Subsequent pushes are faster (only changed layers upload).

### Image not showing on Docker Hub

**Solution:** Wait 1-2 minutes after push, then refresh. Check for push errors in terminal output.

## Docker Hub Limits (Free Tier)

- Unlimited public repositories
- Pull rate limit: 100 pulls per 6 hours (anonymous)
- Pull rate limit: 200 pulls per 6 hours (authenticated)
- Storage: No limit on public repositories

For most use cases, the free tier is sufficient!

## Making Your Image Official (Optional)

To get your image featured or certified:

1. Get significant usage (thousands of pulls)
2. Apply for Docker Official Images program
3. Requires meeting security and documentation standards

---

## Quick Reference Commands

```powershell
# Build and tag
docker build -t mrcrunchybeans/youth-secure-checkin:latest .

# Login
docker login

# Push
docker push mrcrunchybeans/youth-secure-checkin:latest

# Pull (others)
docker pull mrcrunchybeans/youth-secure-checkin:latest

# Check local images
docker images | Select-String youth-secure-checkin

# Remove local image
docker rmi mrcrunchybeans/youth-secure-checkin:latest
```

---

## Next Steps

After publishing:

1. ✅ Update GitHub README with Docker Hub badge and instructions
2. ✅ Add Docker Hub link to project documentation
3. ✅ Test pulling from fresh machine
4. ✅ Share with community!
5. ✅ Monitor pulls and feedback on Docker Hub

Your Docker image is now publicly available for anyone to use! 🎉
