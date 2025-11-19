# Quick Start Guide - Docker Demo

## Launch the Demo

```bash
# Start demo instance (with auto-reset)
docker-compose --profile demo up -d

# View logs
docker-compose logs -f demo-app

# Access at http://localhost:5000
```

## Test Credentials

**Admin Login:**
- Username: `demo`
- Password: `demo123`

**Test Families (Phone Lookup):**
- 555-0101 - Johnson family (2 kids)
- 555-0102 - Smith family (1 kid)  
- 555-0103 - Williams family (2 kids)
- 555-0105 - Garcia family (3 kids)

## Stop the Demo

```bash
docker-compose --profile demo down
```

## Full Documentation

See [DOCKER_DEMO_README.md](DOCKER_DEMO_README.md) for complete instructions.
