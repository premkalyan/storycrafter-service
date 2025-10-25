# StoryCrafter MCP

MCP wrapper for the StoryCrafter AI-powered backlog generator.

## Overview

StoryCrafter MCP provides Model Context Protocol (MCP) tools for generating comprehensive project backlogs from VISHKAR 3-agent consensus discussions.

## Architecture

```
┌──────────────────┐
│  Vishkar Agent   │
└────────┬─────────┘
         │ MCP Protocol
┌────────▼─────────────┐
│ StoryCrafter MCP     │ (Next.js wrapper - this repo)
│ /api/mcp             │
└────────┬─────────────┘
         │ HTTP
┌────────▼─────────────┐
│ StoryCrafter Service │ (Python/FastAPI)
│ - Claude Sonnet 4.5  │ (epic structure)
│ - GPT-5              │ (story details)
└──────────────────────┘
```

## MCP Tools

### 1. generate_backlog

Generate complete project backlog from consensus discussion.

**Input**:
```json
{
  "consensus_messages": [
    {"role": "system", "content": "Project: ..."},
    {"role": "alex", "content": "Product requirements..."},
    {"role": "blake", "content": "Technical architecture..."},
    {"role": "casey", "content": "Project constraints..."}
  ],
  "project_metadata": {
    "project_name": "My Project",
    "timeline": "8 weeks",
    "team_size": "3 developers"
  },
  "use_full_context": true
}
```

**Output**:
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
    "epics": [
      {
        "id": "EPIC-1",
        "title": "Authentication & User Management",
        "stories": [...]
      }
    ]
  }
}
```

### 2. get_backlog_summary

Get summary statistics from generated backlog.

**Input**:
```json
{
  "backlog": { ... }
}
```

**Output**:
```json
{
  "project_name": "My Project",
  "total_epics": 8,
  "total_stories": 36,
  "total_estimated_hours": 458,
  "epics_breakdown": [...]
}
```

## Deployment

### Prerequisites

1. StoryCrafter service deployed at `STORYCRAFTER_SERVICE_URL`
2. Vercel account

### Deploy MCP Wrapper

```bash
cd /Users/premkalyan/code/mcp/storycrafter-mcp
npm install
vercel --prod --yes
```

### Environment Variables

Set in Vercel dashboard or `vercel.json`:

- `STORYCRAFTER_SERVICE_URL` - URL of deployed StoryCrafter service (default: https://storycrafter-service.vercel.app)

## Usage

### Via HTTP (Direct)

```bash
# List tools
curl https://storycrafter-mcp.vercel.app/api/mcp

# Generate backlog
curl -X POST https://storycrafter-mcp.vercel.app/api/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "method": "tools/call",
    "params": {
      "tool": "generate_backlog",
      "arguments": {
        "consensus_messages": [
          {"role": "system", "content": "Project: Test App"},
          {"role": "alex", "content": "We need user auth"},
          {"role": "blake", "content": "Use JWT"},
          {"role": "casey", "content": "4 weeks, 2 devs"}
        ]
      }
    }
  }'
```

### Via Vishkar Agent

Vishkar automatically discovers this MCP through the registry and calls it when needed.

**Example conversation**:

> **User**: "Generate a backlog for a task management app with offline support"
>
> **Vishkar**:
> 1. Loads VISHKAR 3-agent discussion from context
> 2. Calls `generate_backlog` with consensus messages
> 3. Returns structured backlog with epics and stories

## Integration with Enhanced Context MCP

Update `/Users/premkalyan/code/mcp/enhanced-context-mcp/public/mcp-registry.json`:

```json
{
  "mcpServers": {
    "storycrafter": {
      "name": "StoryCrafter MCP",
      "url": "https://storycrafter-mcp.vercel.app",
      "description": "AI-powered backlog generator for VISHKAR consensus. Generates 6-8 epics with 20-40 detailed stories from 3-agent discussions.",
      "transport": "http",
      "tools": [
        {
          "name": "generate_backlog",
          "description": "Generate complete backlog from VISHKAR consensus messages",
          "endpoint": "/api/mcp",
          "method": "POST"
        },
        {
          "name": "get_backlog_summary",
          "description": "Get summary statistics from generated backlog",
          "endpoint": "/api/mcp",
          "method": "POST"
        }
      ]
    }
  }
}
```

## Cost

**Per Backlog Generation**:
- Claude Sonnet 4.5: ~$0.15 (epic structure)
- GPT-5: ~$0.29 (story expansion)
- **Total**: ~$0.44

**Monthly** (100 backlogs):
- API costs: ~$44
- Vercel: Free tier or $20/mo Pro

## Testing

```bash
# Install dependencies
npm install

# Run locally
npm run dev

# Test endpoint
curl http://localhost:3000/api/mcp

# Test with sample consensus
curl -X POST http://localhost:3000/api/mcp \
  -H "Content-Type: application/json" \
  -d @test_request.json
```

## Troubleshooting

### "StoryCrafter service unavailable"

Check `STORYCRAFTER_SERVICE_URL` environment variable points to deployed service.

### "Backlog generation failed"

Verify StoryCrafter service has valid `ANTHROPIC_API_KEY` and `OPENAI_API_KEY`.

### Timeout errors

Backlog generation takes 30-60 seconds. Increase timeout in calling code if needed.

## Related

- **StoryCrafter Service**: `/Users/premkalyan/code/Services/StoryCrafter`
- **MCP Registry**: `/Users/premkalyan/code/mcp/enhanced-context-mcp/public/mcp-registry.json`
- **VISHKAR Guide**: `/Users/premkalyan/code/mcp/enhanced-context-mcp/VISHKAR-MCP-INTEGRATION-GUIDE.md`
