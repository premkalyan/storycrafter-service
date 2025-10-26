# StoryCrafter API Request Reference

Complete guide to the request/response format for all 4 tool endpoints.

---

## 1. POST /generate-epics

**Purpose:** Generate epic structure from consensus messages (Phase 1)

### Request Format

```typescript
interface GenerateEpicsRequest {
  consensus_messages: ConsensusMessage[];  // REQUIRED
  project_metadata?: ProjectMetadata;      // OPTIONAL
}

interface ConsensusMessage {
  role: "system" | "alex" | "blake" | "casey";
  content: string;
}

interface ProjectMetadata {
  project_name?: string;
  project_description?: string;
  target_users?: string;
  platform?: string;
  timeline?: string;
  team_size?: string;
}
```

### Working Example

```bash
curl -X POST https://storycrafter-service.vercel.app/generate-epics \
  -H "Content-Type: application/json" \
  -d '{
    "consensus_messages": [
      {
        "role": "system",
        "content": "Project: Task Manager App"
      },
      {
        "role": "alex",
        "content": "We need task CRUD and dashboard"
      },
      {
        "role": "blake",
        "content": "React frontend, Node.js backend"
      },
      {
        "role": "casey",
        "content": "8 weeks with 2 developers"
      }
    ],
    "project_metadata": {
      "project_name": "Task Manager",
      "timeline": "8 weeks"
    }
  }'
```

### Success Response (200)

```json
{
  "success": true,
  "epics": [
    {
      "id": "EPIC-1",
      "title": "User Authentication",
      "description": "Implement user auth system",
      "priority": "High",
      "category": "MVP",
      "story_count_target": 4
    }
  ],
  "metadata": {
    "total_epics": 8,
    "generated_at": "2025-10-26T13:21:18.329229Z"
  }
}
```

### Error Response (422 - Validation Error)

```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "consensus_messages"],
      "msg": "Field required",
      "input": {}
    }
  ]
}
```

### Error Response (400/500 - Processing Error)

```json
{
  "detail": "Epic generation failed: <error message>"
}
```

---

## 2. POST /generate-stories

**Purpose:** Generate detailed stories for a specific epic (Phase 2)

### Request Format

```typescript
interface GenerateStoriesRequest {
  epic: Epic;                           // REQUIRED
  consensus_messages: ConsensusMessage[]; // REQUIRED
  project_metadata?: ProjectMetadata;    // OPTIONAL
}

interface Epic {
  id: string;
  title: string;
  description: string;
  priority: string;
  category: string;
  story_count_target?: number; // default: 4
}
```

### Working Example

```bash
curl -X POST https://storycrafter-service.vercel.app/generate-stories \
  -H "Content-Type: application/json" \
  -d '{
    "epic": {
      "id": "EPIC-1",
      "title": "User Authentication",
      "description": "Implement user authentication system",
      "priority": "High",
      "category": "MVP",
      "story_count_target": 4
    },
    "consensus_messages": [
      {
        "role": "system",
        "content": "Project: Task Manager App"
      }
    ]
  }'
```

### Success Response (200)

```json
{
  "success": true,
  "stories": [
    {
      "id": "EPIC-1-1",
      "title": "User Registration",
      "description": "As a user, I want to register...",
      "acceptance_criteria": [
        "User can enter email and password",
        "System validates email format"
      ],
      "technical_tasks": [
        "Create registration API",
        "Build registration form"
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
    "generated_at": "2025-10-26T13:21:18.329229Z"
  }
}
```

---

## 3. POST /regenerate-epic

**Purpose:** Regenerate an epic based on user feedback

### Request Format

```typescript
interface RegenerateEpicRequest {
  epic: Epic;                           // REQUIRED
  user_feedback: string;                // REQUIRED
  consensus_messages: ConsensusMessage[]; // REQUIRED
  project_metadata?: ProjectMetadata;    // OPTIONAL
}
```

### Working Example

```bash
curl -X POST https://storycrafter-service.vercel.app/regenerate-epic \
  -H "Content-Type: application/json" \
  -d '{
    "epic": {
      "id": "EPIC-1",
      "title": "User Authentication",
      "description": "Basic auth system",
      "priority": "High",
      "category": "MVP"
    },
    "user_feedback": "Focus on OAuth instead of email/password",
    "consensus_messages": [
      {
        "role": "system",
        "content": "Project: Task Manager App"
      }
    ]
  }'
```

### Success Response (200)

```json
{
  "success": true,
  "epic": {
    "id": "EPIC-1",
    "title": "OAuth Social Authentication",
    "description": "Implement OAuth with Google and GitHub",
    "priority": "High",
    "category": "MVP",
    "story_count_target": 4,
    "regeneration_notes": "Updated to focus on OAuth per user feedback"
  },
  "metadata": {
    "regenerated_at": "2025-10-26T13:21:18.329229Z"
  }
}
```

---

## 4. POST /regenerate-story

**Purpose:** Regenerate a story based on user feedback

### Request Format

```typescript
interface RegenerateStoryRequest {
  epic: Epic;                           // REQUIRED (for context)
  story: Story;                         // REQUIRED
  user_feedback: string;                // REQUIRED
  consensus_messages: ConsensusMessage[]; // REQUIRED
  project_metadata?: ProjectMetadata;    // OPTIONAL
}

interface Story {
  id: string;
  title: string;
  description?: string;
  acceptance_criteria?: string[];
  technical_tasks?: string[];
  priority?: string; // default: "P1"
  story_points?: number; // default: 0
  estimated_hours?: number; // default: 0
  dependencies?: string[];
  tags?: string[];
  layer?: string; // default: "fullstack"
}
```

### Working Example

```bash
curl -X POST https://storycrafter-service.vercel.app/regenerate-story \
  -H "Content-Type: application/json" \
  -d '{
    "epic": {
      "id": "EPIC-1",
      "title": "User Authentication",
      "description": "Auth system",
      "priority": "High",
      "category": "MVP"
    },
    "story": {
      "id": "EPIC-1-1",
      "title": "User Registration",
      "description": "As a user, I want to register",
      "acceptance_criteria": ["Can enter email"],
      "technical_tasks": ["Create API"],
      "priority": "P0",
      "story_points": 5,
      "estimated_hours": 10
    },
    "user_feedback": "Add email verification requirement",
    "consensus_messages": [
      {
        "role": "system",
        "content": "Project: Task Manager App"
      }
    ]
  }'
```

### Success Response (200)

```json
{
  "success": true,
  "story": {
    "id": "EPIC-1-1",
    "title": "User Registration with Email Verification",
    "description": "As a user, I want to register with email verification",
    "acceptance_criteria": [
      "User can enter email and password",
      "Verification email sent on registration",
      "User cannot login until email verified"
    ],
    "technical_tasks": [
      "Create registration API",
      "Implement email verification service",
      "Build verification UI flow"
    ],
    "priority": "P0",
    "story_points": 8,
    "estimated_hours": 16,
    "dependencies": [],
    "tags": ["mvp", "backend", "frontend", "security"],
    "layer": "fullstack",
    "regeneration_notes": "Added email verification per feedback"
  },
  "metadata": {
    "regenerated_at": "2025-10-26T13:21:18.329229Z"
  }
}
```

---

## Common Issues & Debugging

### Issue 1: "Field required" Validation Error (422)

**Cause:** Missing required field in request

**Debug:**
```bash
# Check your request has ALL required fields
# For generate-epics:
{
  "consensus_messages": [...] // MUST be present
}
```

### Issue 2: "[object Object]" Error

**Cause:** Frontend not properly handling error response

**Debug:**
```javascript
// Wrong:
console.log(error); // Shows [object Object]

// Right:
console.log(error.message);
console.log(JSON.stringify(error));
console.log(error.response?.data?.detail);
```

### Issue 3: 500 Internal Server Error

**Cause:** API key issues or service error

**Check Vercel Logs:**
1. Go to https://vercel.com/dashboard
2. Select storycrafter-service project
3. Click "Logs" tab
4. Look for the actual error message

**Common causes:**
- Missing ANTHROPIC_API_KEY or OPENAI_API_KEY
- Invalid API keys
- Rate limit exceeded
- JSON parsing error

---

## Testing Your Request

### Quick Test (verify format):

```bash
# Test your exact request format:
curl -X POST https://storycrafter-service.vercel.app/generate-epics \
  -H "Content-Type: application/json" \
  -d @your-request.json \
  -v  # verbose mode shows full request/response
```

### Validate JSON:

```bash
# Ensure JSON is valid:
cat your-request.json | jq .
# If this errors, your JSON is malformed
```

### Check Required Fields:

```bash
# For generate-epics, minimum valid request:
{
  "consensus_messages": [
    {"role": "system", "content": "test"}
  ]
}
```

---

## VISHKAR Integration Checklist

When calling from VISHKAR, ensure:

1. ✅ **Correct URL:** `https://storycrafter-service.vercel.app/generate-epics`
2. ✅ **Content-Type header:** `application/json`
3. ✅ **Required fields present:**
   - `consensus_messages` array with at least 1 message
   - Each message has `role` and `content`
4. ✅ **Error handling:**
   - Catch errors properly
   - Log `error.response?.data?.detail` for API errors
   - Log `error.message` for network errors
5. ✅ **Response parsing:**
   - Check `response.data.success === true`
   - Access epics via `response.data.epics`
   - Access metadata via `response.data.metadata`

---

## Need Help?

1. **Test your request directly with curl** (see examples above)
2. **Check Vercel logs** for server-side errors
3. **Validate your JSON** with `jq` or online validator
4. **Compare your request** to working examples in this document
