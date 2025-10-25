# Check Vercel Build Logs (Not Runtime Logs)

## Important: Build Logs vs Runtime Logs

You're seeing **runtime errors**, but we need to check **BUILD logs** to verify if Mangum was actually installed.

---

## How to Check Build Logs in Vercel

### Step 1: Go to Deployments

1. https://vercel.com/dashboard
2. Click on `storycrafter-service` project
3. Click on **Deployments** tab

### Step 2: Find Latest Deployment

Look for deployment with commit: **"Fix: Move Mangum import to top of file"**

Should have:
- ✅ Green checkmark (successful build)
- Commit SHA starting with `f7b...` or similar
- Time: After 14:54

### Step 3: Click on the Deployment

Click on the deployment row (not the "..." menu)

### Step 4: View Build Logs

You'll see sections:
1. **Building** ← CLICK HERE
2. **Deploying**
3. **Running**

In the **Building** section, look for:

```
Installing dependencies from requirements.txt
Collecting anthropic>=0.69.0
Collecting openai>=1.0.0
Collecting python-dotenv==1.0.0
Collecting fastapi>=0.109.0
Collecting uvicorn>=0.27.0
Collecting pydantic>=2.6.0
Collecting mangum>=0.17.0    ← CHECK THIS LINE!
```

### What to Look For

**✅ Good Signs**:
```
Successfully installed mangum-0.17.0
Building with @vercel/python
Build Completed
```

**❌ Bad Signs**:
```
ERROR: Could not find a version that satisfies mangum
Failed to install dependencies
```

---

## Current Deployed Version Check

Also check which Git commit is actually deployed:

1. In deployment details, look for **"Source"**
2. Should show: `premkalyan/storycrafter-service @ <commit-hash>`
3. Click the commit hash
4. Verify it shows the latest code with Mangum import at top

---

## Alternative: Check Live Code

Vercel shows the actual deployed code:

1. In deployment, go to **"Source"** tab
2. Navigate to `main.py`
3. Check line 13: Should have `from mangum import Mangum`
4. Check line 197: Should have `handler = Mangum(app, lifespan="off")`

---

## If Mangum Not Installed

If build logs show Mangum wasn't installed:

### Possible Issues

1. **Old deployment cached**: Force redeploy
2. **requirements.txt not updated**: Check file in GitHub
3. **Build cache issue**: Clear and rebuild

### Solution

1. Go to **Settings** → **General**
2. Scroll to **Build & Development Settings**
3. Click **"Edit"**
4. Toggle **"Override"** for Install Command
5. Set: `pip install -r requirements.txt --no-cache-dir`
6. Save and redeploy

---

## Runtime Logs (What You're Seeing)

Your current logs show:
```
File "/var/task/vc__handler__python.py", line 242, in <module>
    if not issubclass(base, BaseHTTPRequestHandler):
TypeError: issubclass() arg 1 must be a class
```

This means:
- ❌ Either Mangum not installed
- ❌ Or handler still = app (not wrapped with Mangum)
- ❌ Or old deployment still active

**Solution**: Check build logs to verify Mangum installation!

---

## Quick Verification Script

After new deployment completes, test:

```bash
# Check if endpoint exists (should return JSON, not HTML error)
curl -I https://storycrafter-service.vercel.app/

# If you get HTML 404 = wrong runtime
# If you get JSON 200 = correct runtime with Mangum!
```

---

## Deployment Timeline

- 14:51 - First Mangum fix committed
- 14:53 - Runtime logs still show error (old deployment or import issue)
- 14:54 - Import moved to top, pushed
- 14:55+ - **New deployment should be building NOW**

**Check build logs for deployment after 14:54!**
