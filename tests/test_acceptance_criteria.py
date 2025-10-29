"""
Unit tests for Acceptance Criteria validation and generation
Tests the enhanced acceptance criteria feature
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from storycrafter_service import VISHKARStoryCrafterService


class TestAcceptanceCriteriaValidation:
    """Test acceptance criteria validation logic"""

    @pytest.fixture
    def service(self):
        """Create service instance with mock API keys"""
        with patch.dict(os.environ, {
            'ANTHROPIC_API_KEY': 'test-key',
            'OPENAI_API_KEY': 'test-key'
        }):
            return VISHKARStoryCrafterService()

    def test_validate_high_quality_criteria(self, service):
        """Test validation of high-quality acceptance criteria"""
        criteria = [
            "GIVEN user is logged in WHEN they click submit THEN form is validated",
            "System validates email format and displays error message",
            "User can complete registration within 3 seconds",
            "[Edge case]: System handles duplicate email by showing friendly error",
            "[Non-functional]: Password meets security requirements (min 8 chars, 1 special char)"
        ]

        validation = service._validate_acceptance_criteria(criteria, "TEST-1")

        assert validation["is_valid"] is True
        assert validation["total_criteria"] == 5
        assert validation["quality_score"] >= 3
        assert validation["quality_indicators"]["has_given_when_then"] is True
        assert validation["quality_indicators"]["has_edge_cases"] is True
        assert validation["quality_indicators"]["has_non_functional"] is True

    def test_validate_low_quality_criteria(self, service):
        """Test validation of low-quality acceptance criteria"""
        criteria = [
            "User can login",
            "Form works correctly",
            "System is fast"
        ]

        validation = service._validate_acceptance_criteria(criteria, "TEST-2")

        assert validation["is_valid"] is False  # Less than 4 criteria
        assert validation["total_criteria"] == 3
        assert validation["quality_score"] < 2
        assert len(validation["warnings"]) > 0

    def test_validate_insufficient_criteria(self, service):
        """Test validation with too few criteria"""
        criteria = [
            "User can submit form",
            "System validates input"
        ]

        validation = service._validate_acceptance_criteria(criteria, "TEST-3")

        assert validation["is_valid"] is False
        assert "Less than 4 acceptance criteria" in validation["warnings"][0]

    def test_validate_excessive_criteria(self, service):
        """Test validation with too many criteria"""
        criteria = ["Criterion " + str(i) for i in range(15)]

        validation = service._validate_acceptance_criteria(criteria, "TEST-4")

        assert validation["is_valid"] is True  # Still valid, just warning
        assert any("More than 10 criteria" in w for w in validation["warnings"])

    def test_validate_empty_criteria(self, service):
        """Test validation with empty criteria list"""
        criteria = []

        validation = service._validate_acceptance_criteria(criteria, "TEST-5")

        assert validation["is_valid"] is False
        assert validation["total_criteria"] == 0
        assert "Less than 4 acceptance criteria" in validation["warnings"][0]

    def test_quality_indicators_given_when_then(self, service):
        """Test detection of Given-When-Then format"""
        criteria = [
            "GIVEN user is on homepage WHEN they click button THEN modal opens",
            "System validates data",
            "User completes action",
            "Edge case handled"
        ]

        validation = service._validate_acceptance_criteria(criteria, "TEST-6")

        assert validation["quality_indicators"]["has_given_when_then"] is True

    def test_quality_indicators_edge_cases(self, service):
        """Test detection of edge cases"""
        criteria = [
            "User completes registration",
            "System validates email",
            "[Edge case]: System handles network timeout gracefully",
            "Error message displayed for invalid input",
            "Performance meets requirements"
        ]

        validation = service._validate_acceptance_criteria(criteria, "TEST-7")

        assert validation["quality_indicators"]["has_edge_cases"] is True

    def test_quality_indicators_non_functional(self, service):
        """Test detection of non-functional requirements"""
        criteria = [
            "User logs in successfully",
            "System validates credentials",
            "[Non-functional]: Response time < 2 seconds",
            "[Security]: Passwords encrypted at rest",
            "Error handling implemented"
        ]

        validation = service._validate_acceptance_criteria(criteria, "TEST-8")

        assert validation["quality_indicators"]["has_non_functional"] is True

    def test_quality_indicators_validation(self, service):
        """Test detection of specific validation requirements"""
        criteria = [
            "User submits form",
            "System validates email format and domain",
            "System verifies password strength",
            "Confirmation message displayed",
            "Edge case handled"
        ]

        validation = service._validate_acceptance_criteria(criteria, "TEST-9")

        assert validation["quality_indicators"]["has_specific_validation"] is True

    def test_validate_backlog_all_stories(self, service):
        """Test validation of all stories in a backlog"""
        backlog = {
            "epics": [
                {
                    "id": "EPIC-1",
                    "stories": [
                        {
                            "id": "EPIC-1-1",
                            "acceptance_criteria": [
                                "GIVEN user is logged in WHEN they submit THEN data is saved",
                                "System validates input",
                                "[Edge case]: Handles network error",
                                "[Non-functional]: Performance < 1s",
                                "User receives confirmation"
                            ]
                        },
                        {
                            "id": "EPIC-1-2",
                            "acceptance_criteria": [
                                "User can login",
                                "System works"  # Low quality
                            ]
                        }
                    ]
                }
            ]
        }

        # Should not raise exception, just log warnings
        service._validate_backlog_acceptance_criteria(backlog)

    def test_validate_multiple_epics(self, service):
        """Test validation across multiple epics"""
        backlog = {
            "epics": [
                {
                    "id": "EPIC-1",
                    "stories": [
                        {
                            "id": "EPIC-1-1",
                            "acceptance_criteria": [
                                "GIVEN precondition WHEN action THEN result",
                                "System validates data",
                                "[Edge case]: Handles error",
                                "[Non-functional]: Fast performance",
                                "User gets feedback"
                            ]
                        }
                    ]
                },
                {
                    "id": "EPIC-2",
                    "stories": [
                        {
                            "id": "EPIC-2-1",
                            "acceptance_criteria": [
                                "Feature works",
                                "User happy",
                                "System stable"
                            ]
                        }
                    ]
                }
            ]
        }

        # Should validate all stories across epics
        service._validate_backlog_acceptance_criteria(backlog)


class TestAcceptanceCriteriaGeneration:
    """Test that generated stories include detailed acceptance criteria"""

    @pytest.fixture
    def service(self):
        """Create service instance with mock API keys"""
        with patch.dict(os.environ, {
            'ANTHROPIC_API_KEY': 'test-key',
            'OPENAI_API_KEY': 'test-key'
        }):
            return VISHKARStoryCrafterService()

    @pytest.mark.asyncio
    async def test_generated_story_has_acceptance_criteria(self, service):
        """Test that generated stories include acceptance criteria"""
        epic = {
            "id": "EPIC-1",
            "title": "User Authentication",
            "description": "Implement user auth system",
            "priority": "High",
            "category": "MVP",
            "story_count_target": 1
        }

        mock_response = Mock()
        mock_response.content = [Mock(text='''[
            {
                "id": "EPIC-1-1",
                "title": "User Login",
                "description": "As a user, I want to login",
                "acceptance_criteria": [
                    "GIVEN user on login page WHEN enters valid credentials THEN logged in",
                    "System validates email format",
                    "User sees error for invalid credentials",
                    "[Edge case]: System handles expired session",
                    "[Non-functional]: Login completes in < 2 seconds"
                ],
                "technical_tasks": ["Create login API", "Build login form"],
                "priority": "P0",
                "story_points": 5,
                "estimated_hours": 10,
                "dependencies": [],
                "tags": ["mvp"],
                "layer": "fullstack"
            }
        ]'''
        )]

        with patch.object(service.anthropic_client.messages, 'create', return_value=mock_response):
            stories = await service._generate_stories_for_epic_claude(
                epic,
                "Project context",
                None
            )

            assert len(stories) == 1
            assert "acceptance_criteria" in stories[0]
            assert len(stories[0]["acceptance_criteria"]) >= 4

    @pytest.mark.asyncio
    async def test_regenerated_story_has_enhanced_criteria(self, service):
        """Test that regenerated stories have enhanced acceptance criteria"""
        epic = {
            "id": "EPIC-1",
            "title": "User Auth",
            "description": "Auth system"
        }

        story = {
            "id": "EPIC-1-1",
            "title": "Login",
            "description": "User login feature",
            "acceptance_criteria": [
                "User can login",
                "Password validated"
            ]
        }

        mock_response = Mock()
        mock_response.content = [Mock(text='''{
            "id": "EPIC-1-1",
            "title": "User Login Enhanced",
            "description": "As a user, I want to securely login",
            "acceptance_criteria": [
                "GIVEN user on login page WHEN enters valid email and password THEN successfully authenticated",
                "System validates email format and displays specific error messages",
                "User can complete login within 2 seconds",
                "[Edge case]: System handles incorrect password by locking account after 5 attempts",
                "[Non-functional]: Passwords are encrypted using bcrypt with salt",
                "User receives clear feedback for all error scenarios"
            ],
            "technical_tasks": ["Update login API", "Enhance validation"],
            "priority": "P0",
            "story_points": 5,
            "estimated_hours": 10,
            "dependencies": [],
            "tags": ["mvp"],
            "layer": "fullstack",
            "regeneration_notes": "Enhanced acceptance criteria with specific details"
        }'''
        )]

        with patch.object(service.anthropic_client.messages, 'create', return_value=mock_response):
            regenerated = await service._regenerate_single_story_claude(
                epic,
                story,
                "Add more detailed acceptance criteria",
                "Project context",
                None
            )

            assert "acceptance_criteria" in regenerated
            assert len(regenerated["acceptance_criteria"]) >= 5

            # Validate the enhanced criteria
            validation = service._validate_acceptance_criteria(
                regenerated["acceptance_criteria"],
                regenerated["id"]
            )
            assert validation["quality_score"] >= 3


class TestAcceptanceCriteriaInPrompts:
    """Test that prompts correctly request detailed acceptance criteria"""

    @pytest.fixture
    def service(self):
        """Create service instance with mock API keys"""
        with patch.dict(os.environ, {
            'ANTHROPIC_API_KEY': 'test-key',
            'OPENAI_API_KEY': 'test-key'
        }):
            return VISHKARStoryCrafterService()

    def test_legacy_prompt_mentions_acceptance_criteria(self, service):
        """Test that legacy prompt includes acceptance criteria requirements"""
        requirements = {
            "project_name": "Test Project",
            "project_description": "Test description",
            "mvp_features": ["Feature 1", "Feature 2"]
        }

        prompt = service._build_claude_prompt(requirements)

        assert "ACCEPTANCE CRITERIA" in prompt.upper()
        assert "4-7" in prompt or "DETAILED" in prompt.upper()

    def test_prompt_includes_quality_guidelines(self, service):
        """Test that prompts include quality guidelines for acceptance criteria"""
        requirements = {
            "project_name": "Test Project",
            "mvp_features": []
        }

        prompt = service._build_claude_prompt(requirements)

        # Should mention Given-When-Then or quality requirements
        assert any(term in prompt for term in [
            "Given-When-Then",
            "testable",
            "measurable",
            "edge case",
            "non-functional"
        ])
