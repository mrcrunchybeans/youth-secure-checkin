# Demo Quick Reference

## 🚀 Launch Demo (1 Command)

```bash
docker-compose --profile demo up -d
```

Then open: **http://localhost:5000**

## 🔐 Login

**Admin:**
- Username: `demo`
- Password: `demo123`

## 📱 Test Families

Use these phone numbers in the check-in interface:

| Phone | Family | Kids | Notes |
|-------|--------|------|-------|
| 555-0101 | Johnson | Emma, Noah (2) | Peanut allergy |
| 555-0102 | Smith | Olivia (1) | Asthma inhaler |
| 555-0103 | Williams | Liam, Sophia (2) | Vegetarian |
| 555-0104 | Brown | Mason (1) | - |
| 555-0105 | Garcia | Isabella, Ethan, Ava (3) | Glasses |
| 555-0106 | Martinez | Lucas (1) | - |
| 555-0107 | Anderson | Charlotte, Benjamin (2) | Lactose intolerant |
| 555-0108 | Taylor | Amelia (1) | - |

## 📊 Demo Features

- ✅ 8 families with realistic data
- ✅ 15 scouts with notes
- ✅ 6 events (past & future)
- ✅ Check-in history
- ✅ Auto-reset every 24 hours
- ✅ Demo banner & branding

## 🛑 Stop Demo

```bash
docker-compose --profile demo down
```

## 📖 Full Documentation

- **Quick Start**: [DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md)
- **Full Guide**: [DOCKER_DEMO_README.md](DOCKER_DEMO_README.md)
- **Implementation**: [DOCKER_DEMO_IMPLEMENTATION.md](DOCKER_DEMO_IMPLEMENTATION.md)

---

💡 **Tip**: Database resets every 24 hours automatically to keep demo fresh!
