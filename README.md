# StoryCrafter Service

AI-powered backlog generator for VISHKAR consensus discussions.

## Overview

StoryCrafter transforms 3-agent consensus discussions into comprehensive project backlogs with:
- 6-8 Epics covering all project areas
- 20-40 User Stories with detailed acceptance criteria
- Technical implementation tasks for each story
- Story points and time estimates
- MVP prioritization

## Architecture

**Two-Phase Generation**:
1. **Phase 1**: Claude Sonnet 4.5 generates epic structure (6-8 epics)
2. **Phase 2**: GPT-5 expands each epic with detailed stories (3-6 per epic)

**Why Two Models?**:
- Claude: Excellent at high-level strategic planning (epic structure)
- GPT-5: 128K output tokens + 400K context window for comprehensive story details

## API Endpoints

### POST /generate-backlog

Generate complete backlog from consensus messages.

**Request**:
```json
{
  "consensus_messages": [
    {
      "role": "system",
      "content": "Project: Student Task App..."
    },
    {
      "role": "alex",
      "content": "From a product perspective..."
    },
    {
      "role": "blake",
      "content": "From a technical perspective..."
    },
    {
      "role": "casey",
      "content": "From a project management perspective..."
    }
  ],
  "project_metadata": {
    "project_name": "Student Task App",
    "timeline": "8 weeks",
    "team_size": "2 developers"
  },
  "use_full_context": true
}
```

**Response**:
```json
{
  "success": true,
  "backlog": {
    "project": {
      "name": "Student Task App",
      "description": "...",
      "target_users": "Students",
      "platform": "Web (PWA)"
    },
    "metadata": {
      "total_epics": 8,
      "total_stories": 36,
      "total_estimated_hours": 458,
      "generated_at": "2025-10-25T..."
    },
    "epics": [
      {
        "id": "EPIC-1",
        "title": "Authentication & User Management",
        "description": "...",
        "priority": "High",
        "category": "MVP",
        "stories": [
          {
            "id": "EPIC-1-1",
            "title": "User Registration",
            "description": "As a student, I want to...",
            "acceptance_criteria": ["Given...", "When...", "Then..."],
            "technical_tasks": ["Create auth API", "Build signup form"],
            "priority": "P0",
            "story_points": 5,
            "estimated_hours": 10,
            "tags": ["mvp", "backend", "frontend"],
            "layer": "fullstack"
          }
        ]
      }
    ]
  }
}
```

### GET /health

Health check endpoint.

**Response**:
```json
{
  "status": "healthy",
  "service": "StoryCrafter API",
  "version": "2.0.0"
}
```

## Local Development

### Prerequisites

- Python 3.10+
- Anthropic API key
- OpenAI API key (GPT-5 access)

### Setup

```bash
# Clone and navigate
cd /Users/premkalyan/code/Services/StoryCrafter

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your API keys

# Run locally
python api/index.py
```

### Test Endpoint

```bash
curl http://localhost:8000/health
```

### Test Generation

```bash
curl -X POST http://localhost:8000/generate-backlog \
  -H "Content-Type: application/json" \
  -d '{
    "consensus_messages": [
      {"role": "system", "content": "Project: Test App"},
      {"role": "alex", "content": "We need user authentication"},
      {"role": "blake", "content": "Use JWT for auth"},
      {"role": "casey", "content": "Timeline: 4 weeks"}
    ],
    "use_full_context": true
  }'
```

## Deployment to Vercel

### Prerequisites

- Vercel account
- Vercel CLI (`npm install -g vercel`)

### Deploy

```bash
# Login to Vercel
vercel login

# Set environment variables (secrets)
vercel secrets add anthropic-api-key "sk-ant-your-key"
vercel secrets add openai-api-key "sk-your-openai-key"

# Deploy to production
vercel --prod
```

### Verify Deployment

```bash
# Health check
curl https://your-deployment-url.vercel.app/health

# Test generation
curl -X POST https://your-deployment-url.vercel.app/generate-backlog \
  -H "Content-Type: application/json" \
  -d @test_request.json
```

## Cost Estimates

**Per Backlog Generation**:
- Claude Sonnet 4.5 (epic structure): ~$0.15
- GPT-5 (8 epics × stories): ~$0.29
- **Total**: ~$0.44 per complete backlog

**Monthly (100 backlogs)**:
- ~$44/month for API costs
- Vercel: Free tier (or $20/mo Pro for higher limits)

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | Yes | - | Anthropic API key for Claude |
| `OPENAI_API_KEY` | Yes | - | OpenAI API key for GPT-5 |
| `STORYCRAFTER_CLAUDE_MODEL` | No | claude-sonnet-4-20250514 | Claude model ID |
| `STORYCRAFTER_GPT_MODEL` | No | gpt-5 | GPT model ID |
| `STORYCRAFTER_CLAUDE_MAX_TOKENS` | No | 8192 | Max tokens for Claude |
| `STORYCRAFTER_GPT_MAX_TOKENS` | No | 128000 | Max tokens for GPT |
| `STORYCRAFTER_TEMPERATURE` | No | 0.5 | Generation temperature |

## Integration

This service is designed to be called by:
1. **Vishkar Agent** - Through MCP wrapper
2. **Direct HTTP** - Any client can POST consensus messages
3. **CLI** - Command-line tools

See `/Users/premkalyan/code/mcp/storycrafter-mcp` for MCP wrapper.

## Project Structure

```
/Users/premkalyan/code/Services/StoryCrafter/
├── api/
│   └── index.py              # FastAPI application
├── storycrafter_service.py   # Core service logic
├── requirements.txt          # Python dependencies
├── vercel.json              # Vercel deployment config
├── .env.example             # Environment template
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## Troubleshooting

### "ANTHROPIC_API_KEY must be provided"

Ensure environment variables are set:
- Locally: Add to `.env` file
- Vercel: Set as secrets (`vercel secrets add`)

### "Failed to parse GPT-5 response"

Service automatically falls back to Claude if GPT-5 fails. Check logs for details.

### Low story count (< 20 stories)

Try adjusting `story_count_target` per epic or use `use_full_context: false` for different generation approach.

## License

Part of the Prometheus Framework.
