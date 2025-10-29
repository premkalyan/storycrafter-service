# StoryCrafter Service API Documentation

## Overview

The **StoryCrafter Service** is an AI-powered backlog generator that transforms 3-agent consensus discussions (from VISHKAR/Prometheus) into comprehensive project backlogs with epics and user stories. It generates detailed acceptance criteria, technical tasks, and provides granular control over backlog generation.

**Version**: 2.0
**AI Models**: Claude Sonnet 4.5 (Anthropic) + GPT-5 (OpenAI)

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [API Methods](#api-methods)
3. [Data Formats](#data-formats)
4. [Acceptance Criteria](#acceptance-criteria)
5. [Usage Examples](#usage-examples)
6. [Integration Guide](#integration-guide)
7. [Error Handling](#error-handling)

---

## Quick Start

### Installation

```python
from storycrafter_service import get_storycrafter_service

# Initialize service
service = get_storycrafter_service(
    anthropic_api_key="your-anthropic-key",
    openai_api_key="your-openai-key"
)
```

### Environment Variables

```bash
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...

# Optional: Model configuration
STORYCRAFTER_CLAUDE_MODEL=claude-sonnet-4-20250514
STORYCRAFTER_GPT_MODEL=gpt-5
STORYCRAFTER_CLAUDE_MAX_TOKENS=8192
STORYCRAFTER_GPT_MAX_TOKENS=128000
STORYCRAFTER_TEMPERATURE=0.5
```

---

## API Methods

### 1. `generate_from_consensus()` - Full Backlog Generation

**Purpose**: Generate complete backlog (epics + stories) from consensus messages in one call.

**Signature**:
```python
async def generate_from_consensus(
    consensus_messages: List[Dict[str, str]],
    project_metadata: Dict[str, Any] = None,
    use_full_context: bool = True
) -> Dict[str, Any]
```

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `consensus_messages` | `List[Dict]` | ✅ Yes | Messages from 3-agent VISHKAR discussion |
| `project_metadata` | `Dict` | ❌ No | Project details (name, timeline, team, etc.) |
| `use_full_context` | `bool` | ❌ No | Use full consensus (default: `True`) vs legacy mode |

**Returns**: Complete backlog in VISHKAR format (see [Backlog Format](#backlog-format))

**Example**:
```python
backlog = await service.generate_from_consensus(
    consensus_messages=[
        {"role": "system", "content": "Project: E-commerce Platform"},
        {"role": "alex", "content": "Need user auth and product catalog"},
        {"role": "blake", "content": "Use React + Node.js + PostgreSQL"},
        {"role": "casey", "content": "8 weeks, team of 4 developers"}
    ],
    project_metadata={
        "project_name": "E-commerce Platform",
        "target_users": "Online shoppers",
        "platform": "Web"
    }
)

print(f"Generated {backlog['metadata']['total_epics']} epics")
print(f"Generated {backlog['metadata']['total_stories']} stories")
```

---

### 2. `generate_epics()` - Epic Structure Only (Phase 1)

**Purpose**: Generate epic structure without stories (faster, for initial planning).

**Signature**:
```python
async def generate_epics(
    consensus_messages: List[Dict[str, str]],
    project_metadata: Dict[str, Any] = None
) -> List[Dict[str, Any]]
```

**Returns**: List of epic objects (see [Epic Format](#epic-format))

**Example**:
```python
epics = await service.generate_epics(
    consensus_messages=consensus_messages,
    project_metadata={"project_name": "My App"}
)

for epic in epics:
    print(f"{epic['id']}: {epic['title']} ({epic['priority']})")
```

---

### 3. `generate_stories()` - Stories for Specific Epic (Phase 2)

**Purpose**: Generate detailed stories for a single epic.

**Signature**:
```python
async def generate_stories(
    epic: Dict[str, Any],
    consensus_messages: List[Dict[str, str]],
    project_metadata: Dict[str, Any] = None
) -> List[Dict[str, Any]]
```

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `epic` | `Dict` | ✅ Yes | Epic object to generate stories for |
| `consensus_messages` | `List[Dict]` | ✅ Yes | Full consensus for context |
| `project_metadata` | `Dict` | ❌ No | Project metadata |

**Returns**: List of story objects (see [Story Format](#story-format))

**Example**:
```python
stories = await service.generate_stories(
    epic={
        "id": "EPIC-1",
        "title": "User Authentication",
        "description": "Implement secure user authentication system",
        "priority": "High",
        "category": "MVP"
    },
    consensus_messages=consensus_messages
)

for story in stories:
    print(f"{story['id']}: {story['title']} ({story['story_points']} pts)")
```

---

### 4. `regenerate_epic()` - Regenerate Epic with Feedback

**Purpose**: Regenerate a single epic based on user feedback.

**Signature**:
```python
async def regenerate_epic(
    epic: Dict[str, Any],
    user_feedback: str,
    consensus_messages: List[Dict[str, str]],
    project_metadata: Dict[str, Any] = None
) -> Dict[str, Any]
```

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `epic` | `Dict` | ✅ Yes | Original epic to regenerate |
| `user_feedback` | `str` | ✅ Yes | What needs to change |
| `consensus_messages` | `List[Dict]` | ✅ Yes | Full consensus |
| `project_metadata` | `Dict` | ❌ No | Project metadata |

**Returns**: Regenerated epic object with `regeneration_notes` field

**Example**:
```python
regenerated_epic = await service.regenerate_epic(
    epic=original_epic,
    user_feedback="Make this epic focus more on security aspects and OAuth integration",
    consensus_messages=consensus_messages
)

print(f"Updated: {regenerated_epic['title']}")
print(f"Notes: {regenerated_epic['regeneration_notes']}")
```

---

### 5. `regenerate_story()` - Regenerate Story with Feedback

**Purpose**: Regenerate a single story based on user feedback.

**Signature**:
```python
async def regenerate_story(
    epic: Dict[str, Any],
    story: Dict[str, Any],
    user_feedback: str,
    consensus_messages: List[Dict[str, str]],
    project_metadata: Dict[str, Any] = None
) -> Dict[str, Any]
```

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `epic` | `Dict` | ✅ Yes | Parent epic (for context) |
| `story` | `Dict` | ✅ Yes | Original story to regenerate |
| `user_feedback` | `str` | ✅ Yes | What needs to change |
| `consensus_messages` | `List[Dict]` | ✅ Yes | Full consensus |
| `project_metadata` | `Dict` | ❌ No | Project metadata |

**Returns**: Regenerated story object with `regeneration_notes` field

**Example**:
```python
regenerated_story = await service.regenerate_story(
    epic=parent_epic,
    story=original_story,
    user_feedback="Add more detailed acceptance criteria covering edge cases and error handling",
    consensus_messages=consensus_messages
)

print(f"Updated: {regenerated_story['title']}")
print(f"Acceptance Criteria: {len(regenerated_story['acceptance_criteria'])}")
```

---

## Data Formats

### Backlog Format

**Complete backlog structure returned by `generate_from_consensus()`**:

```json
{
  "project": {
    "name": "E-commerce Platform",
    "description": "Online shopping platform with payment integration",
    "target_users": "Online shoppers",
    "platform": "Web"
  },
  "metadata": {
    "total_epics": 6,
    "total_stories": 24,
    "total_estimated_hours": 480,
    "generated_at": "2025-10-29T10:30:00Z",
    "generator": "StoryCrafter v2.0 (Anthropic + OpenAI)"
  },
  "epics": [
    {
      "id": "EPIC-1",
      "title": "User Authentication & Authorization",
      "description": "Implement secure user authentication system with OAuth 2.0 support",
      "priority": "High",
      "category": "MVP",
      "stories": [
        {
          "id": "EPIC-1-1",
          "title": "User Registration Flow",
          "description": "As a new user, I want to register an account so that I can access the platform",
          "acceptance_criteria": [
            "GIVEN user is on registration page WHEN they enter valid email and password THEN account is created successfully",
            "System validates email format and displays specific error messages for invalid formats",
            "User can complete registration within 3 seconds under normal conditions",
            "[Edge case]: System handles duplicate email by showing friendly error message",
            "[Non-functional]: Password is encrypted using bcrypt with minimum 10 rounds",
            "User receives email verification link within 30 seconds of registration"
          ],
          "technical_tasks": [
            "Create POST /api/auth/register endpoint with validation",
            "Implement bcrypt password hashing with salt",
            "Build registration form component in React",
            "Add email validation service with regex and DNS check",
            "Implement email verification workflow with tokens",
            "Write unit tests for registration logic",
            "Add integration tests for full registration flow"
          ],
          "priority": "P0",
          "story_points": 5,
          "estimated_hours": 10,
          "dependencies": [],
          "tags": ["mvp", "backend", "frontend", "security"],
          "layer": "fullstack"
        }
      ]
    }
  ]
}
```

---

### Epic Format

**Structure returned by `generate_epics()` and contained in backlog**:

```json
{
  "id": "EPIC-1",
  "title": "User Authentication & Authorization",
  "description": "Implement secure user authentication system with OAuth 2.0 support and role-based access control",
  "priority": "High",
  "category": "MVP",
  "story_count_target": 4,
  "stories": []
}
```

**Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `id` | `string` | Unique epic identifier (e.g., "EPIC-1") |
| `title` | `string` | Concise epic title |
| `description` | `string` | Detailed epic description (2-3 sentences) |
| `priority` | `string` | Priority level: `"High"`, `"Medium"`, `"Low"` |
| `category` | `string` | Category: `"MVP"`, `"Post-MVP"`, `"Technical"` |
| `story_count_target` | `number` | Target number of stories (used during generation) |
| `stories` | `array` | List of story objects (empty in phase 1) |

---

### Story Format

**Structure returned by `generate_stories()` and contained in epics**:

```json
{
  "id": "EPIC-1-1",
  "title": "User Registration Flow",
  "description": "As a new user, I want to register an account so that I can access the platform",
  "acceptance_criteria": [
    "GIVEN user is on registration page WHEN they enter valid email and password THEN account is created successfully",
    "System validates email format and displays specific error messages for invalid formats",
    "User can complete registration within 3 seconds under normal conditions",
    "[Edge case]: System handles duplicate email by showing friendly error message",
    "[Non-functional]: Password is encrypted using bcrypt with minimum 10 rounds",
    "User receives email verification link within 30 seconds of registration"
  ],
  "technical_tasks": [
    "Create POST /api/auth/register endpoint with validation",
    "Implement bcrypt password hashing with salt",
    "Build registration form component in React",
    "Add email validation service with regex and DNS check",
    "Implement email verification workflow with tokens",
    "Write unit tests for registration logic",
    "Add integration tests for full registration flow"
  ],
  "priority": "P0",
  "story_points": 5,
  "estimated_hours": 10,
  "dependencies": ["EPIC-2-1"],
  "tags": ["mvp", "backend", "frontend", "security"],
  "layer": "fullstack"
}
```

**Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `id` | `string` | Unique story identifier (e.g., "EPIC-1-1") |
| `title` | `string` | Concise story title |
| `description` | `string` | User story in format: "As a [persona], I want [goal], so that [benefit]" |
| `acceptance_criteria` | `array` | **4-7 detailed testable conditions** (see [Acceptance Criteria](#acceptance-criteria)) |
| `technical_tasks` | `array` | 4-7 specific implementation tasks |
| `priority` | `string` | Story priority: `"P0"` (critical), `"P1"` (high), `"P2"` (medium), `"P3"` (low) |
| `story_points` | `number` | Fibonacci points: `2`, `3`, `5`, `8`, `13` |
| `estimated_hours` | `number` | Development time estimate in hours |
| `dependencies` | `array` | List of story IDs this depends on |
| `tags` | `array` | Labels: `"mvp"`, `"backend"`, `"frontend"`, `"database"`, `"security"`, etc. |
| `layer` | `string` | Architecture layer: `"fullstack"`, `"backend"`, `"frontend"`, `"database"`, `"infrastructure"` |

---

## Acceptance Criteria

### Overview

StoryCrafter generates **detailed, high-quality acceptance criteria** for every user story. Each story includes **4-7 criteria** that are:

- ✅ **Specific and testable**
- ✅ **Measurable with clear conditions**
- ✅ **Following industry best practices**
- ✅ **Covering edge cases and error scenarios**
- ✅ **Including non-functional requirements**

### Format Types

#### 1. Given-When-Then Format (BDD Style)
```
"GIVEN user is logged in WHEN they click submit button THEN form is validated and saved"
```

#### 2. Validation Requirements
```
"System validates email format and displays specific error message for invalid input"
```

#### 3. Performance/Time Constraints
```
"User can complete checkout process within 5 seconds under normal network conditions"
```

#### 4. Edge Cases
```
"[Edge case]: System handles network timeout by auto-saving form data and retrying"
```

#### 5. Non-Functional Requirements
```
"[Non-functional]: API response time < 200ms for 95th percentile under load"
"[Security]: User passwords encrypted using bcrypt with minimum 12 rounds"
"[Usability]: Error messages are clear and actionable in user's preferred language"
```

### Quality Indicators

The service validates acceptance criteria quality using **4 quality indicators**:

| Indicator | Description | Example Keywords |
|-----------|-------------|------------------|
| **Given-When-Then** | BDD-style format | "given", "when", "then" |
| **Edge Cases** | Error/failure scenarios | "edge case", "error", "failure", "timeout" |
| **Non-Functional** | Performance/security/usability | "performance", "security", "usability", "accessibility" |
| **Validation** | Specific verification | "validate", "verify", "check" |

**Quality Score**: 0-4 (one point per indicator present)

### Validation

The service automatically validates acceptance criteria during generation:

```python
# Automatic validation logs
[StoryCrafter] Validating acceptance criteria quality...
[StoryCrafter] ✅ All 24 stories have quality acceptance criteria

# Or if quality issues detected:
[StoryCrafter] ⚠️  Acceptance Criteria Validation: 3/24 stories have quality warnings
[StoryCrafter]   - Story EPIC-1-2: Less than 4 acceptance criteria (found 2)
[StoryCrafter]   - Story EPIC-2-1: Low quality score (1/4). Consider adding Given-When-Then format, edge cases, or non-functional requirements.
```

### Example: High-Quality Acceptance Criteria

```json
"acceptance_criteria": [
  "GIVEN user is on product page WHEN they click 'Add to Cart' THEN product appears in cart with correct quantity",
  "System validates product availability in real-time and displays stock status",
  "User can add item to cart within 1 second under normal conditions",
  "[Edge case]: System handles out-of-stock items by showing waitlist option and notification signup",
  "[Edge case]: System prevents duplicate cart entries by incrementing quantity instead",
  "[Non-functional]: Cart update operation completes in < 200ms for 99% of requests",
  "[Security]: Cart data persisted securely with user session encryption"
]
```

---

## Usage Examples

### Example 1: Generate Complete Backlog

```python
import asyncio
from storycrafter_service import get_storycrafter_service

async def main():
    service = get_storycrafter_service()

    # Consensus from VISHKAR 3-agent discussion
    consensus = [
        {"role": "system", "content": "Project: Task Management App"},
        {"role": "alex", "content": "Users need task creation, assignment, and tracking"},
        {"role": "blake", "content": "Tech stack: React, FastAPI, PostgreSQL"},
        {"role": "casey", "content": "Timeline: 6 weeks, Team: 3 developers"}
    ]

    # Generate complete backlog
    backlog = await service.generate_from_consensus(
        consensus_messages=consensus,
        project_metadata={
            "project_name": "Task Manager Pro",
            "target_users": "Project managers and teams",
            "platform": "Web + Mobile"
        }
    )

    # Access results
    print(f"Total Epics: {backlog['metadata']['total_epics']}")
    print(f"Total Stories: {backlog['metadata']['total_stories']}")
    print(f"Total Hours: {backlog['metadata']['total_estimated_hours']}")

    # Iterate through epics
    for epic in backlog['epics']:
        print(f"\n{epic['id']}: {epic['title']}")
        for story in epic['stories']:
            print(f"  └─ {story['id']}: {story['title']} ({story['story_points']} pts)")
            print(f"     Acceptance Criteria: {len(story['acceptance_criteria'])}")

asyncio.run(main())
```

---

### Example 2: Two-Phase Generation (Epics → Stories)

```python
async def two_phase_generation():
    service = get_storycrafter_service()

    consensus = [...]  # Your consensus messages

    # Phase 1: Generate epic structure
    print("Phase 1: Generating epics...")
    epics = await service.generate_epics(consensus)

    # User reviews epics, selects which ones to expand
    selected_epic = epics[0]  # First epic

    # Phase 2: Generate stories for selected epic
    print(f"Phase 2: Generating stories for {selected_epic['title']}...")
    stories = await service.generate_stories(
        epic=selected_epic,
        consensus_messages=consensus
    )

    # Add stories to epic
    selected_epic['stories'] = stories

    return selected_epic

asyncio.run(two_phase_generation())
```

---

### Example 3: Regenerate Story with User Feedback

```python
async def improve_story():
    service = get_storycrafter_service()

    # Existing story
    original_story = {
        "id": "EPIC-1-1",
        "title": "User Login",
        "description": "As a user, I want to login",
        "acceptance_criteria": [
            "User can enter credentials",
            "System validates login"
        ],
        # ... other fields
    }

    # User feedback
    feedback = """
    This story needs more detailed acceptance criteria:
    1. Add Given-When-Then format for clarity
    2. Include edge cases for failed login attempts
    3. Add performance requirements
    4. Specify security requirements for password handling
    """

    # Regenerate with feedback
    improved_story = await service.regenerate_story(
        epic=parent_epic,
        story=original_story,
        user_feedback=feedback,
        consensus_messages=consensus
    )

    # Check improvements
    print(f"Original criteria count: {len(original_story['acceptance_criteria'])}")
    print(f"Improved criteria count: {len(improved_story['acceptance_criteria'])}")
    print(f"\nNew acceptance criteria:")
    for criterion in improved_story['acceptance_criteria']:
        print(f"  - {criterion}")

asyncio.run(improve_story())
```

---

## Integration Guide

### REST API Integration

If you're calling StoryCrafter via REST API (FastAPI):

**Endpoint**: `POST /generate-from-consensus`

**Request**:
```json
{
  "consensus_messages": [
    {"role": "system", "content": "Project: My App"},
    {"role": "alex", "content": "Product requirements..."},
    {"role": "blake", "content": "Technical architecture..."},
    {"role": "casey", "content": "Timeline and resources..."}
  ],
  "project_metadata": {
    "project_name": "My App",
    "platform": "Web"
  }
}
```

**Response**:
```json
{
  "success": true,
  "backlog": {
    "project": {...},
    "metadata": {...},
    "epics": [...]
  },
  "metadata": {
    "generated_at": "2025-10-29T10:30:00Z",
    "total_epics": 6,
    "total_stories": 24
  }
}
```

### Frontend Integration

```typescript
// TypeScript interfaces
interface AcceptanceCriterion {
  text: string;
  type: 'given-when-then' | 'validation' | 'performance' | 'edge-case' | 'non-functional';
}

interface Story {
  id: string;
  title: string;
  description: string;
  acceptance_criteria: string[];
  technical_tasks: string[];
  priority: 'P0' | 'P1' | 'P2' | 'P3';
  story_points: number;
  estimated_hours: number;
  dependencies: string[];
  tags: string[];
  layer: 'fullstack' | 'backend' | 'frontend' | 'database' | 'infrastructure';
}

interface Epic {
  id: string;
  title: string;
  description: string;
  priority: 'High' | 'Medium' | 'Low';
  category: 'MVP' | 'Post-MVP' | 'Technical';
  stories: Story[];
}

interface Backlog {
  project: {
    name: string;
    description: string;
    target_users: string;
    platform: string;
  };
  metadata: {
    total_epics: number;
    total_stories: number;
    total_estimated_hours: number;
    generated_at: string;
    generator: string;
  };
  epics: Epic[];
}

// Fetch backlog
async function generateBacklog(consensusMessages: any[]): Promise<Backlog> {
  const response = await fetch('/api/generate-from-consensus', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ consensus_messages: consensusMessages })
  });

  const data = await response.json();
  return data.backlog;
}
```

---

## Error Handling

### Common Errors

#### 1. Missing API Keys
```python
ValueError: ANTHROPIC_API_KEY must be provided or set in environment
```
**Solution**: Set environment variables or pass keys to constructor

#### 2. Invalid Consensus Format
```python
# Ensure messages have 'role' and 'content'
consensus = [
    {"role": "system", "content": "..."},  # ✅ Correct
    {"role": "alex", "content": "..."},
]
```

#### 3. JSON Parse Errors
```python
ValueError: Failed to parse backlog JSON: Expecting property name enclosed in double quotes
```
**Solution**: This is handled internally; if it persists, check AI model responses

#### 4. Low-Quality Acceptance Criteria
```python
# Not an error, but logged as warning:
[StoryCrafter] ⚠️  Story EPIC-1-1: Low quality score (1/4)
```
**Solution**: Use `regenerate_story()` with feedback requesting more detailed criteria

### Best Practices

1. **Always await async methods**:
   ```python
   backlog = await service.generate_from_consensus(...)  # ✅ Correct
   ```

2. **Provide full consensus context**:
   - Include system message with project overview
   - Include messages from all 3 agents (Alex, Blake, Casey)
   - More context = better backlog quality

3. **Use project metadata**:
   ```python
   project_metadata = {
       "project_name": "...",
       "target_users": "...",
       "platform": "...",
       "timeline": "...",
       "team_size": "..."
   }
   ```

4. **Validate acceptance criteria**:
   - Check `quality_score` in validation results
   - Regenerate stories with quality score < 2

5. **Handle rate limits**:
   - Claude API: 50 requests/min (default)
   - OpenAI GPT-5: Varies by tier
   - Add retry logic with exponential backoff

---

## Configuration

### Model Selection

```bash
# Use different Claude model
export STORYCRAFTER_CLAUDE_MODEL=claude-sonnet-4-20250514

# Adjust token limits
export STORYCRAFTER_CLAUDE_MAX_TOKENS=8192
export STORYCRAFTER_GPT_MAX_TOKENS=128000

# Adjust creativity (0.0-1.0)
export STORYCRAFTER_TEMPERATURE=0.5
```

### Generation Modes

```python
# Full context mode (recommended)
backlog = await service.generate_from_consensus(
    consensus_messages=messages,
    use_full_context=True  # Default
)

# Legacy mode (uses requirement extraction)
backlog = await service.generate_from_consensus(
    consensus_messages=messages,
    use_full_context=False
)
```

---

## Performance

### Timing Estimates

| Operation | Duration | Notes |
|-----------|----------|-------|
| `generate_epics()` | 5-15 sec | 6-8 epics |
| `generate_stories()` per epic | 10-30 sec | 3-6 stories per epic |
| `generate_from_consensus()` | 60-180 sec | Full backlog (6 epics, 24+ stories) |
| `regenerate_epic()` | 5-10 sec | Single epic |
| `regenerate_story()` | 5-10 sec | Single story |

### Optimization Tips

1. **Use two-phase generation** for large projects:
   - Generate epics first
   - Let users review/modify
   - Generate stories only for selected epics

2. **Parallel story generation**:
   ```python
   import asyncio

   # Generate stories for multiple epics in parallel
   story_tasks = [
       service.generate_stories(epic, consensus)
       for epic in selected_epics
   ]

   all_stories = await asyncio.gather(*story_tasks)
   ```

3. **Cache consensus context**:
   - Format consensus once
   - Reuse for multiple operations

---

## Support

For issues, feature requests, or questions:
- **GitHub**: [storyCrafter-service](https://github.com/premkalyan/storycrafter-service)
- **Email**: [your-support-email]

---

**Last Updated**: 2025-10-29
**Version**: 2.0
**License**: MIT
