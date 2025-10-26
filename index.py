"""
StoryCrafter FastAPI Service - Vercel Deployment
"""

from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
import os
import sys

from storycrafter_service import get_storycrafter_service

# Initialize FastAPI app
app = FastAPI(
    title="StoryCrafter API",
    description="AI-powered backlog generator for VISHKAR consensus discussions",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# REQUEST/RESPONSE MODELS
# ============================================================

class ConsensusMessage(BaseModel):
    """Single message in consensus discussion"""
    role: str = Field(..., description="Role: system, alex, blake, casey")
    content: str = Field(..., description="Message content")


class ProjectMetadata(BaseModel):
    """Optional project metadata"""
    project_name: Optional[str] = None
    project_description: Optional[str] = None
    target_users: Optional[str] = None
    platform: Optional[str] = None
    timeline: Optional[str] = None
    team_size: Optional[str] = None


class GenerateBacklogRequest(BaseModel):
    """Request to generate backlog from consensus"""
    consensus_messages: List[ConsensusMessage] = Field(
        ...,
        description="List of messages from 3-agent consensus discussion"
    )
    project_metadata: Optional[ProjectMetadata] = None
    use_full_context: bool = Field(
        default=True,
        description="Use full context mode (recommended)"
    )


class GenerateEpicsRequest(BaseModel):
    """Request to generate epic structure"""
    consensus_messages: List[ConsensusMessage] = Field(
        ...,
        description="List of messages from 3-agent consensus discussion"
    )
    project_metadata: Optional[ProjectMetadata] = None


class EpicModel(BaseModel):
    """Epic object"""
    id: str
    title: str
    description: str
    priority: str
    category: str
    story_count_target: Optional[int] = 4


class GenerateStoriesRequest(BaseModel):
    """Request to generate stories for an epic"""
    epic: EpicModel = Field(..., description="Epic to generate stories for")
    consensus_messages: List[ConsensusMessage] = Field(
        ...,
        description="List of messages from 3-agent consensus discussion"
    )
    project_metadata: Optional[ProjectMetadata] = None


class RegenerateEpicRequest(BaseModel):
    """Request to regenerate an epic"""
    epic: EpicModel = Field(..., description="Original epic to regenerate")
    user_feedback: str = Field(..., description="User feedback on what to change")
    consensus_messages: List[ConsensusMessage] = Field(
        ...,
        description="List of messages from 3-agent consensus discussion"
    )
    project_metadata: Optional[ProjectMetadata] = None


class StoryModel(BaseModel):
    """Story object"""
    id: str
    title: str
    description: Optional[str] = None
    acceptance_criteria: Optional[List[str]] = []
    technical_tasks: Optional[List[str]] = []
    priority: Optional[str] = "P1"
    story_points: Optional[int] = 0
    estimated_hours: Optional[int] = 0
    dependencies: Optional[List[str]] = []
    tags: Optional[List[str]] = []
    layer: Optional[str] = "fullstack"


class RegenerateStoryRequest(BaseModel):
    """Request to regenerate a story"""
    epic: EpicModel = Field(..., description="Parent epic for context")
    story: StoryModel = Field(..., description="Original story to regenerate")
    user_feedback: str = Field(..., description="User feedback on what to change")
    consensus_messages: List[ConsensusMessage] = Field(
        ...,
        description="List of messages from 3-agent consensus discussion"
    )
    project_metadata: Optional[ProjectMetadata] = None


# ============================================================
# ENDPOINTS
# ============================================================

@app.get("/")
async def root():
    """Root endpoint - health check"""
    return {
        "status": "healthy",
        "service": "StoryCrafter API",
        "version": "2.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "StoryCrafter API",
        "version": "2.0.0"
    }


@app.post("/generate-backlog")
async def generate_backlog(
    request: GenerateBacklogRequest,
    x_api_key: Optional[str] = Header(None)
):
    """Generate complete backlog from VISHKAR consensus discussion"""
    try:
        # Get service
        service = get_storycrafter_service()

        # Convert Pydantic models to dicts
        messages = [msg.model_dump() for msg in request.consensus_messages]
        metadata = request.project_metadata.model_dump() if request.project_metadata else None

        # Generate backlog
        backlog = await service.generate_from_consensus(
            consensus_messages=messages,
            project_metadata=metadata,
            use_full_context=request.use_full_context
        )

        return {
            "success": True,
            "backlog": backlog,
            "metadata": {
                "total_epics": backlog['metadata']['total_epics'],
                "total_stories": backlog['metadata']['total_stories'],
                "total_estimated_hours": backlog['metadata']['total_estimated_hours'],
                "generated_at": backlog['metadata']['generated_at']
            }
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Backlog generation failed: {str(e)}"
        )


@app.get("/test")
async def test_endpoint():
    """Test endpoint to verify API is running"""
    return {
        "message": "StoryCrafter API is running",
        "anthropic_key_set": bool(os.getenv('ANTHROPIC_API_KEY')),
        "openai_key_set": bool(os.getenv('OPENAI_API_KEY')),
        "python_version": sys.version
    }


@app.post("/generate-epics")
async def generate_epics(
    request: GenerateEpicsRequest,
    x_api_key: Optional[str] = Header(None)
):
    """Generate epic structure from consensus discussion"""
    try:
        service = get_storycrafter_service()

        # Convert Pydantic models to dicts
        messages = [msg.model_dump() for msg in request.consensus_messages]
        metadata = request.project_metadata.model_dump() if request.project_metadata else None

        # Generate epics
        epics = await service.generate_epics(
            consensus_messages=messages,
            project_metadata=metadata
        )

        return {
            "success": True,
            "epics": epics,
            "metadata": {
                "total_epics": len(epics),
                "generated_at": datetime.utcnow().isoformat() + "Z"
            }
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Epic generation failed: {str(e)}"
        )


@app.post("/generate-stories")
async def generate_stories(
    request: GenerateStoriesRequest,
    x_api_key: Optional[str] = Header(None)
):
    """Generate stories for a specific epic"""
    try:
        service = get_storycrafter_service()

        # Convert Pydantic models to dicts
        epic = request.epic.model_dump()
        messages = [msg.model_dump() for msg in request.consensus_messages]
        metadata = request.project_metadata.model_dump() if request.project_metadata else None

        # Generate stories
        stories = await service.generate_stories(
            epic=epic,
            consensus_messages=messages,
            project_metadata=metadata
        )

        return {
            "success": True,
            "stories": stories,
            "metadata": {
                "epic_id": epic.get('id'),
                "total_stories": len(stories),
                "generated_at": datetime.utcnow().isoformat() + "Z"
            }
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Story generation failed: {str(e)}"
        )


@app.post("/regenerate-epic")
async def regenerate_epic(
    request: RegenerateEpicRequest,
    x_api_key: Optional[str] = Header(None)
):
    """Regenerate an epic based on user feedback"""
    try:
        service = get_storycrafter_service()

        # Convert Pydantic models to dicts
        epic = request.epic.model_dump()
        messages = [msg.model_dump() for msg in request.consensus_messages]
        metadata = request.project_metadata.model_dump() if request.project_metadata else None

        # Regenerate epic
        regenerated_epic = await service.regenerate_epic(
            epic=epic,
            user_feedback=request.user_feedback,
            consensus_messages=messages,
            project_metadata=metadata
        )

        return {
            "success": True,
            "epic": regenerated_epic,
            "metadata": {
                "regenerated_at": datetime.utcnow().isoformat() + "Z"
            }
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Epic regeneration failed: {str(e)}"
        )


@app.post("/regenerate-story")
async def regenerate_story(
    request: RegenerateStoryRequest,
    x_api_key: Optional[str] = Header(None)
):
    """Regenerate a story based on user feedback"""
    try:
        service = get_storycrafter_service()

        # Convert Pydantic models to dicts
        epic = request.epic.model_dump()
        story = request.story.model_dump()
        messages = [msg.model_dump() for msg in request.consensus_messages]
        metadata = request.project_metadata.model_dump() if request.project_metadata else None

        # Regenerate story
        regenerated_story = await service.regenerate_story(
            epic=epic,
            story=story,
            user_feedback=request.user_feedback,
            consensus_messages=messages,
            project_metadata=metadata
        )

        return {
            "success": True,
            "story": regenerated_story,
            "metadata": {
                "regenerated_at": datetime.utcnow().isoformat() + "Z"
            }
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Story regeneration failed: {str(e)}"
        )
