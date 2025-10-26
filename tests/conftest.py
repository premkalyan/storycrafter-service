"""
Pytest configuration and fixtures for StoryCrafter tests
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from index import app


@pytest.fixture
def client():
    """FastAPI test client"""
    return TestClient(app)


@pytest.fixture
def sample_consensus_messages():
    """Sample consensus messages for testing"""
    return [
        {
            "role": "system",
            "content": "Project: Test App - A simple test application"
        },
        {
            "role": "alex",
            "content": "We need user authentication and a dashboard."
        },
        {
            "role": "blake",
            "content": "Use React frontend and Node.js backend."
        },
        {
            "role": "casey",
            "content": "Timeline is 4 weeks with 2 developers."
        }
    ]


@pytest.fixture
def sample_project_metadata():
    """Sample project metadata for testing"""
    return {
        "project_name": "Test App",
        "project_description": "Simple test application",
        "target_users": "Developers",
        "platform": "Web",
        "timeline": "4 weeks",
        "team_size": "2 developers"
    }


@pytest.fixture
def sample_epic():
    """Sample epic for testing"""
    return {
        "id": "EPIC-1",
        "title": "User Authentication",
        "description": "Implement user authentication system",
        "priority": "High",
        "category": "MVP",
        "story_count_target": 4
    }


@pytest.fixture
def sample_story():
    """Sample story for testing"""
    return {
        "id": "EPIC-1-1",
        "title": "User Registration",
        "description": "As a user, I want to register an account",
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
        "tags": ["mvp", "backend"],
        "layer": "fullstack"
    }


@pytest.fixture
def mock_anthropic_client():
    """Mock Anthropic client for testing"""
    mock_client = Mock()
    mock_response = Mock()
    mock_response.content = [Mock(text='{"epics": []}')]
    mock_client.messages.create = Mock(return_value=mock_response)
    return mock_client


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing"""
    mock_client = Mock()
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content='{"stories": []}'))]
    mock_client.chat.completions.create = Mock(return_value=mock_response)
    return mock_client
