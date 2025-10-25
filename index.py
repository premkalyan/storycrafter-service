"""
StoryCrafter FastAPI Service - Vercel Deployment
"""

from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
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
