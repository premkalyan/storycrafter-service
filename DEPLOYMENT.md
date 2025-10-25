# StoryCrafter Deployment Guide

## Prerequisites

1. Vercel account (sign up at https://vercel.com)
2. Vercel CLI installed: `npm install -g vercel`
3. Anthropic API key (for Claude Sonnet 4.5)
4. OpenAI API key (for GPT-5)

## Step 1: Login to Vercel

```bash
vercel login
```

Follow the prompts to authenticate.

## Step 2: Set Environment Variable Secrets

```bash
# Set Anthropic API key
vercel secrets add anthropic-api-key "your-anthropic-key-here"

# Set OpenAI API key
vercel secrets add openai-api-key "your-openai-key-here"
```

**Note**: The secrets are referenced in `vercel.json` as:
- `@anthropic-api-key`
- `@openai-api-key`

## Step 3: Deploy to Production

```bash
cd /Users/premkalyan/code/Services/StoryCrafter
vercel --prod --yes
```

This will:
1. Build the Python FastAPI application
2. Deploy to Vercel serverless functions
3. Configure environment variables from secrets
4. Return the production URL

## Step 4: Verify Deployment

```bash
# Replace with your actual deployment URL
DEPLOYMENT_URL="https://storycrafter-xxx.vercel.app"

# Health check
curl $DEPLOYMENT_URL/health

# Test generation (requires API keys to be set)
curl -X POST $DEPLOYMENT_URL/generate-backlog \
  -H "Content-Type: application/json" \
  -d @test_request.json
```

## Expected Output

**Health Check**:
```json
{
  "status": "healthy",
  "service": "StoryCrafter API",
  "version": "2.0.0"
}
```

**Backlog Generation** (takes 30-60 seconds):
```json
{
  "success": true,
  "backlog": {
    "project": {...},
    "metadata": {
      "total_epics": 8,
      "total_stories": 36,
      "total_estimated_hours": 458
    },
    "epics": [...]
  }
}
```

## Troubleshooting

### "The specified token is not valid"

Run `vercel login` to generate a new authentication token.

### "Environment variables not set"

Ensure secrets are created:
```bash
vercel secrets ls
```

Should show:
- anthropic-api-key
- openai-api-key

### "Module not found" errors

Check `vercel.json` is properly configured with Python runtime.

### Deployment too large

Increase `maxLambdaSize` in `vercel.json` (currently 50mb).

## Manual Deployment via Vercel Dashboard

1. Go to https://vercel.com/dashboard
2. Click "Add New" → "Project"
3. Import from Git: `/Users/premkalyan/code/Services/StoryCrafter`
4. Configure:
   - Framework: Other
   - Root Directory: ./
   - Build Command: (leave empty)
   - Output Directory: (leave empty)
5. Add Environment Variables:
   - `ANTHROPIC_API_KEY` → your key
   - `OPENAI_API_KEY` → your key
6. Deploy

## Cost Estimates

**Per Deployment**:
- Vercel: Free tier (10 serverless functions)
- Or Vercel Pro: $20/month (unlimited)

**Per API Call**:
- Claude Sonnet 4.5: ~$0.15
- GPT-5: ~$0.29
- **Total**: ~$0.44 per backlog generation

**Monthly (100 backlogs)**:
- API costs: ~$44
- Vercel: Free or $20/mo Pro

## Next Steps

After successful deployment:
1. Note the deployment URL
2. Test with `curl` commands above
3. Create MCP wrapper at `/Users/premkalyan/code/mcp/storycrafter-mcp`
4. Update MCP registry with StoryCrafter URL
5. Integrate with Vishkar agent
