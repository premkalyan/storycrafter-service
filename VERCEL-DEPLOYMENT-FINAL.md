# Vercel Deployment - Final Configuration

## ✅ Changes Applied

Restructured to match **proven working examples** from FastAPI + Vercel tutorials.

### File Structure (Now Correct)

```
storycrafter-service/
├── main.py                   # ✅ FastAPI app at ROOT level
├── storycrafter_service.py   # ✅ Core service
├── requirements.txt          # ✅ Dependencies
├── vercel.json              # ✅ Points to main.py
├── .vercelignore            # ✅ Excludes unnecessary files
└── api/                     # Old structure (can delete later)
    └── index.py
```

### vercel.json (Current)

```json
{
  "builds": [
    {
      "src": "main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "main.py"
    }
  ]
}
```

### requirements.txt

```
anthropic>=0.69.0
openai>=1.0.0
python-dotenv==1.0.0
fastapi>=0.109.0
uvicorn>=0.27.0
pydantic>=2.6.0
```

---

## 🚀 Deploy in Vercel (Step-by-Step)

### Step 1: Delete Old Project (If Exists)

1. Go to https://vercel.com/dashboard
2. Find `storycrafter-service` project
3. Settings → General → Scroll to bottom → "Delete Project"

### Step 2: Import Fresh

1. Click **"Add New..."** → **"Project"**
2. Find **`premkalyan/storycrafter-service`** repo
3. Click **"Import"**

### Step 3: Configure (CRITICAL!)

**Framework Preset**: Select **"Other"** ⚠️ NOT Next.js!

**Build Settings**:
- Build Command: (leave empty)
- Output Directory: (leave empty)
- Install Command: (leave empty)
- Root Directory: `./`

### Step 4: Environment Variables

Add these TWO required variables:

| Name | Value | Required |
|------|-------|----------|
| `ANTHROPIC_API_KEY` | `sk-ant-your-key...` | ✅ YES |
| `OPENAI_API_KEY` | `sk-your-openai-key...` | ✅ YES |

**Where to get keys**:
- Anthropic: https://console.anthropic.com/settings/keys
- OpenAI: https://platform.openai.com/api-keys

### Step 5: Deploy

1. Click **"Deploy"**
2. Wait 2-3 minutes
3. Should see ✅ "Deployment Ready"

---

## ✅ Validation Tests

### Test 1: Health Check

```bash
curl https://storycrafter-service.vercel.app/
```

**Expected**:
```json
{
  "status": "healthy",
  "service": "StoryCrafter API",
  "version": "2.0.0"
}
```

**If you get**: HTML or 404 → Still detecting as Next.js (check framework preset)

### Test 2: API Key Status

```bash
curl https://storycrafter-service.vercel.app/test
```

**Expected**:
```json
{
  "message": "StoryCrafter API is running",
  "anthropic_key_set": true,
  "openai_key_set": true,
  "python_version": "3.9.x"
}
```

**If false**: Environment variables not set in Vercel dashboard

### Test 3: Generate Backlog (Full Test - 30-60 seconds)

```bash
curl -X POST https://storycrafter-service.vercel.app/generate-backlog \
  -H "Content-Type: application/json" \
  -d '{
    "consensus_messages": [
      {
        "role": "system",
        "content": "Project: Test Application - A simple app for testing StoryCrafter"
      },
      {
        "role": "alex",
        "content": "We need: user authentication, dashboard, and basic CRUD operations"
      },
      {
        "role": "blake",
        "content": "Use React frontend, Node.js backend, PostgreSQL database"
      },
      {
        "role": "casey",
        "content": "Timeline: 4 weeks with 2 developers"
      }
    ],
    "use_full_context": true
  }' | jq '{success: .success, epics: .metadata.total_epics, stories: .metadata.total_stories}'
```

**Expected output**:
```json
{
  "success": true,
  "epics": 6,
  "stories": 24
}
```

---

## 🔍 Debug: Check Vercel Build Logs

If deployment fails:

1. Go to **Deployments** → Click the failed deployment
2. Click **"Building"** section
3. Look for:

**✅ Good**:
```
Detected Python
Installing dependencies from requirements.txt
Building with @vercel/python
Building main.py
```

**❌ Bad**:
```
Detected framework: Next.js
Building Next.js application
```

If you see "Next.js", the framework preset is still wrong!

---

## 🎯 Why This Structure Works

### Root-Level main.py

All working Vercel + FastAPI examples use this pattern:
- ✅ `main.py` at root
- ✅ Simple `vercel.json` pointing to `main.py`
- ✅ No nested `api/` directory confusion

### Proven Examples

From web search results:
1. https://github.com/hebertcisco/deploy-python-fastapi-in-vercel
2. https://dev.to/abdadeel/deploying-fastapi-app-on-vercel-serverless-18b1
3. https://blog.logrocket.com/deploying-fastapi-applications-to-vercel/

All use root-level entry point, NOT `api/` subdirectory.

---

## 📋 Checklist Before Deploy

- [x] Code pushed to GitHub (branch: master)
- [x] `main.py` exists at root level
- [x] `vercel.json` points to `main.py`
- [x] `requirements.txt` has all dependencies
- [x] `.vercelignore` excludes test files
- [ ] Vercel project deleted (or new import)
- [ ] Framework preset set to "Other"
- [ ] Environment variables added
- [ ] Deploy clicked
- [ ] Tests pass

---

## 🆘 Still Getting Next.js Detection?

### Nuclear Option: Force Python Detection

Add to `vercel.json`:

```json
{
  "functions": {
    "main.py": {
      "runtime": "python3.9"
    }
  },
  "builds": [
    {
      "src": "main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "main.py"
    }
  ]
}
```

### Alternative: Manual Build Settings

In Vercel dashboard → Settings → General:
- Framework Preset: **Other**
- Build Command: (empty)
- Output Directory: (empty)
- Install Command: `pip install -r requirements.txt`

---

## 🎉 Expected Result

Once deployed correctly:

```bash
$ curl https://storycrafter-service.vercel.app/

{
  "status": "healthy",
  "service": "StoryCrafter API",
  "version": "2.0.0"
}
```

**NOT**:
```html
<!DOCTYPE html>
<html>
  <head>
    <title>404: This page could not be found</title>
  </head>
  ...
</html>
```

---

## 📊 Endpoints Available

Once working:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/health` | GET | Health check (alias) |
| `/test` | GET | API key status |
| `/generate-backlog` | POST | Generate backlog (main endpoint) |

All responses are **JSON** (not HTML).

---

## 🔗 Resources

- **GitHub Repo**: https://github.com/premkalyan/storycrafter-service
- **Latest Commit**: Root-level main.py structure
- **Pattern**: Matches proven Vercel + FastAPI examples

---

**Ready to deploy with the correct root-level structure!** 🚀
