"""
StoryCrafter FastAPI Service
HTTP endpoints for backlog generation
"""

from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import os
import sys
from pathlib import Path
from mangum import Mangum

# Import from same directory (root level)
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
    allow_origins=["*"],  # Configure based on your needs
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


class BacklogResponse(BaseModel):
    """Response with generated backlog"""
    success: bool
    backlog: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    service: str
    version: str


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def validate_api_key(x_api_key: Optional[str] = Header(None)) -> bool:
    """Validate API key (optional for public endpoints)"""
    # For now, no authentication required
    # Can be enhanced later with proper API key validation
    return True


def get_service():
    """Get StoryCrafter service instance"""
    try:
        return get_storycrafter_service()
    except ValueError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Service initialization failed: {str(e)}. Please ensure ANTHROPIC_API_KEY and OPENAI_API_KEY are set."
        )


# ============================================================
# ENDPOINTS
# ============================================================

@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - health check"""
    return {
        "status": "healthy",
        "service": "StoryCrafter API",
        "version": "2.0.0"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "StoryCrafter API",
        "version": "2.0.0"
    }


@app.post("/generate-backlog", response_model=BacklogResponse)
async def generate_backlog(
    request: GenerateBacklogRequest,
    x_api_key: Optional[str] = Header(None)
):
    """
    Generate complete backlog from VISHKAR consensus discussion

    Args:
        request: Request with consensus messages and optional metadata
        x_api_key: Optional API key for authentication

    Returns:
        Complete backlog with epics, stories, acceptance criteria, and tasks
    """
    try:
        # Validate API key (currently optional)
        validate_api_key(x_api_key)

        # Get service
        service = get_service()

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


# ============================================================
# VERCEL SERVERLESS HANDLER
# ============================================================

# Wrap FastAPI with Mangum for serverless deployment
handler = Mangum(app, lifespan="off")


# For local development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
