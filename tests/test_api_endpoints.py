"""
API Endpoint Tests for StoryCrafter
Tests all 4 granular tool endpoints
"""
import pytest
from unittest.mock import patch, AsyncMock


class TestHealthEndpoints:
    """Test health check endpoints"""

    def test_root_endpoint(self, client):
        """Test root endpoint returns healthy status"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "StoryCrafter API"

    def test_health_endpoint(self, client):
        """Test /health endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_test_endpoint(self, client):
        """Test /test endpoint"""
        response = client.get("/test")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "anthropic_key_set" in data
        assert "openai_key_set" in data


class TestGenerateEpicsEndpoint:
    """Test /generate-epics endpoint"""

    @patch('storycrafter_service.VISHKARStoryCrafterService.generate_epics')
    @pytest.mark.asyncio
    async def test_generate_epics_success(
        self,
        mock_generate_epics,
        client,
        sample_consensus_messages,
        sample_project_metadata
    ):
        """Test successful epic generation"""
        # Mock the service method
        mock_epics = [
            {
                "id": "EPIC-1",
                "title": "Test Epic",
                "description": "Test description",
                "priority": "High",
                "category": "MVP",
                "story_count_target": 4
            }
        ]
        mock_generate_epics.return_value = mock_epics

        # Make request
        response = client.post(
            "/generate-epics",
            json={
                "consensus_messages": sample_consensus_messages,
                "project_metadata": sample_project_metadata
            }
        )

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "epics" in data
        assert "metadata" in data
        assert data["metadata"]["total_epics"] == len(mock_epics)

    def test_generate_epics_missing_messages(self, client):
        """Test epic generation with missing consensus messages"""
        response = client.post(
            "/generate-epics",
            json={}
        )
        assert response.status_code == 422  # Validation error


class TestGenerateStoriesEndpoint:
    """Test /generate-stories endpoint"""

    @patch('storycrafter_service.VISHKARStoryCrafterService.generate_stories')
    @pytest.mark.asyncio
    async def test_generate_stories_success(
        self,
        mock_generate_stories,
        client,
        sample_epic,
        sample_consensus_messages
    ):
        """Test successful story generation"""
        # Mock the service method
        mock_stories = [
            {
                "id": "EPIC-1-1",
                "title": "Test Story",
                "description": "As a user, I want...",
                "priority": "P0",
                "story_points": 5
            }
        ]
        mock_generate_stories.return_value = mock_stories

        # Make request
        response = client.post(
            "/generate-stories",
            json={
                "epic": sample_epic,
                "consensus_messages": sample_consensus_messages
            }
        )

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "stories" in data
        assert data["metadata"]["total_stories"] == len(mock_stories)

    def test_generate_stories_missing_epic(self, client, sample_consensus_messages):
        """Test story generation with missing epic"""
        response = client.post(
            "/generate-stories",
            json={"consensus_messages": sample_consensus_messages}
        )
        assert response.status_code == 422


class TestRegenerateEpicEndpoint:
    """Test /regenerate-epic endpoint"""

    @patch('storycrafter_service.VISHKARStoryCrafterService.regenerate_epic')
    @pytest.mark.asyncio
    async def test_regenerate_epic_success(
        self,
        mock_regenerate_epic,
        client,
        sample_epic,
        sample_consensus_messages
    ):
        """Test successful epic regeneration"""
        # Mock the service method
        mock_regenerated = {
            **sample_epic,
            "title": "Updated Epic Title",
            "regeneration_notes": "Updated based on feedback"
        }
        mock_regenerate_epic.return_value = mock_regenerated

        # Make request
        response = client.post(
            "/regenerate-epic",
            json={
                "epic": sample_epic,
                "user_feedback": "Please update the title",
                "consensus_messages": sample_consensus_messages
            }
        )

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "epic" in data
        assert "regenerated_at" in data["metadata"]

    def test_regenerate_epic_missing_feedback(
        self,
        client,
        sample_epic,
        sample_consensus_messages
    ):
        """Test epic regeneration without feedback"""
        response = client.post(
            "/regenerate-epic",
            json={
                "epic": sample_epic,
                "consensus_messages": sample_consensus_messages
            }
        )
        assert response.status_code == 422


class TestRegenerateStoryEndpoint:
    """Test /regenerate-story endpoint"""

    @patch('storycrafter_service.VISHKARStoryCrafterService.regenerate_story')
    @pytest.mark.asyncio
    async def test_regenerate_story_success(
        self,
        mock_regenerate_story,
        client,
        sample_epic,
        sample_story,
        sample_consensus_messages
    ):
        """Test successful story regeneration"""
        # Mock the service method
        mock_regenerated = {
            **sample_story,
            "title": "Updated Story Title",
            "regeneration_notes": "Updated based on feedback"
        }
        mock_regenerate_story.return_value = mock_regenerated

        # Make request
        response = client.post(
            "/regenerate-story",
            json={
                "epic": sample_epic,
                "story": sample_story,
                "user_feedback": "Add more acceptance criteria",
                "consensus_messages": sample_consensus_messages
            }
        )

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "story" in data
        assert "regenerated_at" in data["metadata"]

    def test_regenerate_story_missing_story(
        self,
        client,
        sample_epic,
        sample_consensus_messages
    ):
        """Test story regeneration without story"""
        response = client.post(
            "/regenerate-story",
            json={
                "epic": sample_epic,
                "user_feedback": "Update story",
                "consensus_messages": sample_consensus_messages
            }
        )
        assert response.status_code == 422
