# StoryCrafter Service

AI-powered backlog generator for VISHKAR consensus discussions.

## 📚 Documentation

- **[Complete API Documentation](./DOCUMENTATION.md)** - Comprehensive guide with examples
- **[Quick Reference](./QUICK_REFERENCE.md)** - Cheat sheet for common operations

## Overview

StoryCrafter transforms 3-agent consensus discussions into comprehensive project backlogs with:
- 6-8 Epics covering all project areas
- 20-40 User Stories with **detailed acceptance criteria** (4-7 per story)
- Technical implementation tasks for each story
- Story points and time estimates
- MVP prioritization
- **Automatic quality validation** for acceptance criteria

## Features

### ✅ Detailed Acceptance Criteria
Every user story includes **4-7 high-quality acceptance criteria** with:
- **Given-When-Then** format for clarity
- **Edge cases** and error scenarios
- **Non-functional requirements** (performance, security, usability)
- **Specific validations** with measurable conditions
- **Automatic quality validation** with scoring (0-4)

Example:
```
"GIVEN user is on registration page WHEN they enter valid credentials THEN account is created"
"System validates email format and displays specific error messages"
"[Edge case]: System handles duplicate email by showing friendly error"
"[Non-functional]: Password encrypted using bcrypt with minimum 10 rounds"
```

### 🔄 Granular Control
- Generate complete backlog in one call
- Generate epics only (Phase 1)
- Generate stories for specific epic (Phase 2)
- Regenerate individual epics or stories with user feedback

## Architecture

**Two-Phase Generation**:
1. **Phase 1**: Claude Sonnet 4.5 generates epic structure (6-8 epics)
2. **Phase 2**: Claude Sonnet 4.5 expands each epic with detailed stories (3-6 per epic)

**Quality Validation**:
- Automatic acceptance criteria validation
- Quality scoring based on 4 indicators
- Warnings for low-quality stories

## API Endpoints

### POST /generate-backlog

Generate complete backlog from consensus messages (full workflow).

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

---

## New Tool Endpoints (Granular Control)

These endpoints provide fine-grained control over the backlog generation process, allowing you to generate and regenerate individual components.

### POST /generate-epics

Generate epic structure only (Phase 1 of backlog generation).

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
  }
}
```

**Response**:
```json
{
  "success": true,
  "epics": [
    {
      "id": "EPIC-1",
      "title": "Authentication & User Management",
      "description": "Implement user authentication...",
      "priority": "High",
      "category": "MVP",
      "story_count_target": 4
    }
  ],
  "metadata": {
    "total_epics": 8,
    "generated_at": "2025-10-26T..."
  }
}
```

### POST /generate-stories

Generate stories for a specific epic.

**Request**:
```json
{
  "epic": {
    "id": "EPIC-1",
    "title": "Authentication & User Management",
    "description": "Implement user authentication...",
    "priority": "High",
    "category": "MVP",
    "story_count_target": 4
  },
  "consensus_messages": [
    {
      "role": "system",
      "content": "Project: Student Task App..."
    }
  ],
  "project_metadata": {
    "project_name": "Student Task App"
  }
}
```

**Response**:
```json
{
  "success": true,
  "stories": [
    {
      "id": "EPIC-1-1",
      "title": "User Registration",
      "description": "As a student, I want to...",
      "acceptance_criteria": [
        "Given a new user...",
        "When they submit valid credentials...",
        "Then account is created..."
      ],
      "technical_tasks": [
        "Create user model",
        "Build registration API",
        "Implement form validation",
        "Write unit tests"
      ],
      "priority": "P0",
      "story_points": 5,
      "estimated_hours": 10,
      "dependencies": [],
      "tags": ["mvp", "backend", "frontend"],
      "layer": "fullstack"
    }
  ],
  "metadata": {
    "epic_id": "EPIC-1",
    "total_stories": 4,
    "generated_at": "2025-10-26T..."
  }
}
```

### POST /regenerate-epic

Regenerate an epic based on user feedback.

**Request**:
```json
{
  "epic": {
    "id": "EPIC-1",
    "title": "Authentication & User Management",
    "description": "Implement user authentication...",
    "priority": "High",
    "category": "MVP",
    "story_count_target": 4
  },
  "user_feedback": "Focus more on OAuth integration and social login. Less emphasis on basic email/password auth.",
  "consensus_messages": [
    {
      "role": "system",
      "content": "Project: Student Task App..."
    }
  ],
  "project_metadata": {
    "project_name": "Student Task App"
  }
}
```

**Response**:
```json
{
  "success": true,
  "epic": {
    "id": "EPIC-1",
    "title": "OAuth & Social Authentication",
    "description": "Implement OAuth-based authentication with Google and GitHub...",
    "priority": "High",
    "category": "MVP",
    "story_count_target": 4,
    "regeneration_notes": "Updated to focus on OAuth and social login per user feedback"
  },
  "metadata": {
    "regenerated_at": "2025-10-26T..."
  }
}
```

### POST /regenerate-story

Regenerate a story based on user feedback.

**Request**:
```json
{
  "epic": {
    "id": "EPIC-1",
    "title": "Authentication & User Management",
    "description": "Implement user authentication...",
    "priority": "High",
    "category": "MVP"
  },
  "story": {
    "id": "EPIC-1-1",
    "title": "User Registration",
    "description": "As a student, I want to create an account...",
    "acceptance_criteria": ["Criterion 1", "Criterion 2"],
    "technical_tasks": ["Task 1", "Task 2"],
    "priority": "P0",
    "story_points": 5,
    "estimated_hours": 10
  },
  "user_feedback": "Add acceptance criteria for password strength validation and email verification",
  "consensus_messages": [
    {
      "role": "system",
      "content": "Project: Student Task App..."
    }
  ],
  "project_metadata": {
    "project_name": "Student Task App"
  }
}
```

**Response**:
```json
{
  "success": true,
  "story": {
    "id": "EPIC-1-1",
    "title": "User Registration with Email Verification",
    "description": "As a student, I want to create an account with email verification...",
    "acceptance_criteria": [
      "Password must be at least 8 characters with uppercase, lowercase, and numbers",
      "Email verification link sent upon registration",
      "User cannot login until email is verified",
      "Verification link expires after 24 hours"
    ],
    "technical_tasks": [
      "Implement password strength validator",
      "Create email verification service",
      "Build verification token generation",
      "Add email verification UI flow",
      "Write unit tests for validation logic"
    ],
    "priority": "P0",
    "story_points": 8,
    "estimated_hours": 16,
    "dependencies": [],
    "tags": ["mvp", "backend", "frontend", "security"],
    "layer": "fullstack",
    "regeneration_notes": "Added password validation and email verification per user feedback"
  },
  "metadata": {
    "regenerated_at": "2025-10-26T..."
  }
}
```

---

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
