# StoryCrafter Quick Reference

## 🚀 Quick Start

```python
from storycrafter_service import get_storycrafter_service

service = get_storycrafter_service()

backlog = await service.generate_from_consensus(
    consensus_messages=[
        {"role": "system", "content": "Project: My App"},
        {"role": "alex", "content": "Product requirements"},
        {"role": "blake", "content": "Tech architecture"},
        {"role": "casey", "content": "Timeline & resources"}
    ]
)
```

---

## 📋 API Methods Cheat Sheet

| Method | Use Case | Returns |
|--------|----------|---------|
| `generate_from_consensus()` | Full backlog in one call | Complete backlog with epics + stories |
| `generate_epics()` | Epic structure only (Phase 1) | List of epics (no stories) |
| `generate_stories()` | Stories for specific epic (Phase 2) | List of stories |
| `regenerate_epic()` | Update epic based on feedback | Regenerated epic |
| `regenerate_story()` | Update story based on feedback | Regenerated story |

---

## 📦 Response Formats

### Backlog Structure
```json
{
  "project": {...},
  "metadata": {
    "total_epics": 6,
    "total_stories": 24,
    "total_estimated_hours": 480
  },
  "epics": [...]
}
```

### Epic Object
```json
{
  "id": "EPIC-1",
  "title": "User Authentication",
  "description": "Implement secure auth system",
  "priority": "High",           // High, Medium, Low
  "category": "MVP",             // MVP, Post-MVP, Technical
  "stories": [...]
}
```

### Story Object
```json
{
  "id": "EPIC-1-1",
  "title": "User Registration",
  "description": "As a user, I want to...",
  "acceptance_criteria": [...], // 4-7 detailed criteria
  "technical_tasks": [...],     // 4-7 implementation tasks
  "priority": "P0",             // P0, P1, P2, P3
  "story_points": 5,            // 2, 3, 5, 8, 13
  "estimated_hours": 10,
  "dependencies": [],
  "tags": ["mvp", "backend"],
  "layer": "fullstack"          // fullstack, backend, frontend, database, infrastructure
}
```

---

## ✅ Acceptance Criteria Format

### 5 Types of Criteria

1. **Given-When-Then** (BDD format)
   ```
   "GIVEN user is logged in WHEN they submit form THEN data is saved"
   ```

2. **Validation Requirements**
   ```
   "System validates email format and displays specific error messages"
   ```

3. **Performance Constraints**
   ```
   "User can complete action within 3 seconds"
   ```

4. **Edge Cases**
   ```
   "[Edge case]: System handles network timeout gracefully"
   ```

5. **Non-Functional Requirements**
   ```
   "[Non-functional]: Password encrypted using bcrypt"
   "[Security]: API rate limited to 100 req/min"
   "[Usability]: Error messages in user's language"
   ```

### Quality Score (0-4)
- ✅ Has Given-When-Then format
- ✅ Includes edge cases
- ✅ Has non-functional requirements
- ✅ Specific validation statements

**Target**: Quality score ≥ 3 for high-quality stories

---

## 💡 Common Patterns

### Pattern 1: Generate Complete Backlog
```python
backlog = await service.generate_from_consensus(
    consensus_messages=messages,
    project_metadata={"project_name": "My App"}
)
```

### Pattern 2: Two-Phase (Epic → Stories)
```python
# Phase 1: Epics only
epics = await service.generate_epics(messages)

# Phase 2: Stories for selected epic
stories = await service.generate_stories(
    epic=epics[0],
    consensus_messages=messages
)
```

### Pattern 3: Iterative Refinement
```python
# Generate story
story = await service.generate_stories(epic, messages)[0]

# User reviews and provides feedback
improved_story = await service.regenerate_story(
    epic=epic,
    story=story,
    user_feedback="Add more detailed edge cases",
    consensus_messages=messages
)
```

### Pattern 4: Parallel Story Generation
```python
import asyncio

tasks = [
    service.generate_stories(epic, messages)
    for epic in selected_epics
]

all_stories = await asyncio.gather(*tasks)
```

---

## ⚙️ Configuration

### Environment Variables
```bash
# Required
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...

# Optional
STORYCRAFTER_CLAUDE_MODEL=claude-sonnet-4-20250514
STORYCRAFTER_GPT_MODEL=gpt-5
STORYCRAFTER_CLAUDE_MAX_TOKENS=8192
STORYCRAFTER_TEMPERATURE=0.5
```

### Model Selection
```python
service = get_storycrafter_service(
    anthropic_api_key="...",
    openai_api_key="..."
)
```

---

## 🔍 Validation & Quality

### Automatic Validation
```
[StoryCrafter] Validating acceptance criteria quality...
[StoryCrafter] ✅ All 24 stories have quality acceptance criteria
```

### Quality Warnings
```
[StoryCrafter] ⚠️  3/24 stories have quality warnings
[StoryCrafter]   - Story EPIC-1-2: Less than 4 acceptance criteria (found 2)
[StoryCrafter]   - Story EPIC-2-1: Low quality score (1/4)
```

### Manual Validation
```python
validation = service._validate_acceptance_criteria(
    acceptance_criteria=story["acceptance_criteria"],
    story_id=story["id"]
)

print(f"Quality Score: {validation['quality_score']}/4")
print(f"Valid: {validation['is_valid']}")
```

---

## ⏱️ Performance Estimates

| Operation | Time | Output |
|-----------|------|--------|
| Generate epics | 5-15s | 6-8 epics |
| Generate stories (per epic) | 10-30s | 3-6 stories |
| Full backlog | 60-180s | 6 epics + 24+ stories |
| Regenerate epic | 5-10s | 1 epic |
| Regenerate story | 5-10s | 1 story |

---

## 🐛 Common Issues

### Issue: Missing API keys
```python
ValueError: ANTHROPIC_API_KEY must be provided or set in environment
```
**Fix**: Set environment variables or pass to constructor

### Issue: Low-quality criteria
```
[StoryCrafter] ⚠️  Story has low quality score
```
**Fix**: Use `regenerate_story()` with specific feedback:
```python
story = await service.regenerate_story(
    epic, story,
    user_feedback="Add Given-When-Then format, edge cases, and performance requirements",
    consensus_messages=messages
)
```

### Issue: Too few stories
```
[StoryCrafter] ⚠️  Generated only 12 stories (expected 20+)
```
**Fix**: Provide more detailed consensus messages with specific features

---

## 📊 Story Points Reference

| Points | Complexity | Hours | Example |
|--------|------------|-------|---------|
| 2 | Trivial | 2-4h | Simple form field |
| 3 | Simple | 4-8h | Basic CRUD endpoint |
| 5 | Moderate | 8-16h | User authentication |
| 8 | Complex | 16-24h | Payment integration |
| 13 | Very complex | 24-40h | Real-time chat system |

---

## 🎯 Priority Levels

| Priority | Meaning | Use For |
|----------|---------|---------|
| **P0** | Critical | MVP blockers, core functionality |
| **P1** | High | Important features, major bugs |
| **P2** | Medium | Nice-to-have features |
| **P3** | Low | Future enhancements, polish |

---

## 🏷️ Common Tags

| Tag | Description |
|-----|-------------|
| `mvp` | Minimum Viable Product |
| `backend` | Server-side work |
| `frontend` | Client-side work |
| `database` | Data layer changes |
| `security` | Security-related |
| `performance` | Performance optimization |
| `testing` | Test implementation |
| `devops` | Deployment/infrastructure |

---

## 📚 Full Documentation

For detailed documentation, see [DOCUMENTATION.md](./DOCUMENTATION.md)

---

## 🔗 REST API Quick Reference

### Generate Backlog
```bash
POST /generate-from-consensus
Content-Type: application/json

{
  "consensus_messages": [...],
  "project_metadata": {...}
}
```

### Generate Epics
```bash
POST /generate-epics

{
  "consensus_messages": [...],
  "project_metadata": {...}
}
```

### Generate Stories
```bash
POST /generate-stories

{
  "epic": {...},
  "consensus_messages": [...]
}
```

### Regenerate Epic
```bash
POST /regenerate-epic

{
  "epic": {...},
  "user_feedback": "...",
  "consensus_messages": [...]
}
```

### Regenerate Story
```bash
POST /regenerate-story

{
  "epic": {...},
  "story": {...},
  "user_feedback": "...",
  "consensus_messages": [...]
}
```

---

**For complete examples and integration guides, see [DOCUMENTATION.md](./DOCUMENTATION.md)**
