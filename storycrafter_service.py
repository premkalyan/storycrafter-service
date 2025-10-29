"""
VISHKAR StoryCrafter - AI-Powered Backlog Generator
Transforms 3-agent consensus discussions into comprehensive project backlogs

Part of the Prometheus Framework
"""

from typing import List, Dict, Any
from datetime import datetime
import anthropic
import openai
import json
import re
import os
import asyncio


class VISHKARStoryCrafterService:
    """
    Custom backlog generator optimized for VISHKAR consensus format

    Zero dependencies on external backlog generators
    Full control over prompts and output format
    """

    def __init__(self, anthropic_api_key: str = None, openai_api_key: str = None):
        """
        Initialize StoryCrafter service

        Args:
            anthropic_api_key: Anthropic API key (optional, will use env var if not provided)
            openai_api_key: OpenAI API key (optional, will use env var if not provided)
        """
        # Initialize Anthropic (for epic generation)
        anthropic_key = anthropic_api_key or os.getenv('ANTHROPIC_API_KEY')
        if not anthropic_key:
            raise ValueError("ANTHROPIC_API_KEY must be provided or set in environment")
        self.anthropic_client = anthropic.Anthropic(api_key=anthropic_key)

        # Initialize OpenAI (for story generation with GPT-5)
        openai_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        if not openai_key:
            raise ValueError("OPENAI_API_KEY must be provided or set in environment")
        self.openai_client = openai.OpenAI(api_key=openai_key)

        # Model configurations
        self.claude_model = os.getenv('STORYCRAFTER_CLAUDE_MODEL', 'claude-sonnet-4-20250514')
        self.gpt_model = os.getenv('STORYCRAFTER_GPT_MODEL', 'gpt-5')
        self.claude_max_tokens = int(os.getenv('STORYCRAFTER_CLAUDE_MAX_TOKENS', '8192'))
        self.gpt_max_tokens = int(os.getenv('STORYCRAFTER_GPT_MAX_TOKENS', '128000'))
        self.temperature = float(os.getenv('STORYCRAFTER_TEMPERATURE', '0.5'))

    # ============================================================
    # PUBLIC API
    # ============================================================

    async def generate_from_consensus(
        self,
        consensus_messages: List[Dict[str, str]],
        project_metadata: Dict[str, Any] = None,
        use_full_context: bool = True
    ) -> Dict[str, Any]:
        """
        Main entry point: Generate complete backlog from VISHKAR consensus

        Args:
            consensus_messages: List of messages from 3-agent discussion
            project_metadata: Optional metadata (timeline, team size, etc.)
            use_full_context: If True, passes full consensus to Claude directly (default).
                            If False, uses old approach with requirements extraction.

        Returns:
            Complete backlog in VISHKAR format
        """
        print(f"[StoryCrafter] Starting backlog generation from {len(consensus_messages)} messages")
        print(f"[StoryCrafter] Mode: {'FULL CONTEXT' if use_full_context else 'REQUIREMENTS EXTRACTION'}")

        # Step 1: Extract requirements for metadata (always needed)
        requirements = self._extract_requirements(consensus_messages, project_metadata)

        # Step 2: Generate backlog using Claude API
        if use_full_context:
            # NEW APPROACH: Pass full consensus directly to Claude
            print("[StoryCrafter] Using enhanced full-context generation")
            raw_backlog = await self._generate_with_full_context(consensus_messages, project_metadata)
        else:
            # OLD APPROACH: Use extracted requirements
            print("[StoryCrafter] Using legacy requirements extraction")
            raw_backlog = await self._generate_backlog_with_claude(requirements)

        # Step 3: Validate and parse JSON
        parsed_backlog = self._parse_and_validate(raw_backlog)

        # Step 3.5: Validate acceptance criteria quality
        self._validate_backlog_acceptance_criteria(parsed_backlog)

        # Step 4: Transform to VISHKAR frontend format
        vishkar_format = self._transform_to_vishkar_format(parsed_backlog, requirements)

        print(f"[StoryCrafter] ✅ Generated {vishkar_format['metadata']['total_epics']} epics, "
              f"{vishkar_format['metadata']['total_stories']} stories")

        # Warn if output is still sparse
        if vishkar_format['metadata']['total_stories'] < 20:
            print(f"[StoryCrafter] ⚠️  WARNING: Generated only {vishkar_format['metadata']['total_stories']} stories (expected 20+)")
            print("[StoryCrafter] Epic breakdown:")
            for epic in vishkar_format['epics']:
                print(f"  - {epic['id']}: {len(epic['stories'])} stories")

        return vishkar_format

    async def generate_epics(
        self,
        consensus_messages: List[Dict[str, str]],
        project_metadata: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        PUBLIC API: Generate epic structure from consensus messages

        Args:
            consensus_messages: List of messages from 3-agent discussion
            project_metadata: Optional project metadata

        Returns:
            List of epic objects (without stories)
        """
        print(f"[StoryCrafter] Generating epics from {len(consensus_messages)} messages")

        full_context = self._format_full_consensus_for_prompt(consensus_messages, project_metadata)
        epics_list = await self._generate_epic_structure(full_context, project_metadata)

        print(f"[StoryCrafter] Generated {len(epics_list)} epics")
        return epics_list

    async def generate_stories(
        self,
        epic: Dict[str, Any],
        consensus_messages: List[Dict[str, str]],
        project_metadata: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        PUBLIC API: Generate stories for a specific epic

        Args:
            epic: Epic object to generate stories for
            consensus_messages: List of messages from 3-agent discussion
            project_metadata: Optional project metadata

        Returns:
            List of story objects for the epic
        """
        print(f"[StoryCrafter] Generating stories for epic: {epic.get('id', 'unknown')}")

        full_context = self._format_full_consensus_for_prompt(consensus_messages, project_metadata)
        stories = await self._generate_stories_for_epic(epic, full_context, project_metadata)

        print(f"[StoryCrafter] Generated {len(stories)} stories for {epic.get('id', 'unknown')}")
        return stories

    async def regenerate_epic(
        self,
        epic: Dict[str, Any],
        user_feedback: str,
        consensus_messages: List[Dict[str, str]],
        project_metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        PUBLIC API: Regenerate a single epic based on user feedback

        Args:
            epic: Original epic object to regenerate
            user_feedback: User's comments on what needs to change
            consensus_messages: List of messages from 3-agent discussion
            project_metadata: Optional project metadata

        Returns:
            Regenerated epic object
        """
        print(f"[StoryCrafter] Regenerating epic: {epic.get('id', 'unknown')}")

        full_context = self._format_full_consensus_for_prompt(consensus_messages, project_metadata)
        regenerated_epic = await self._regenerate_single_epic(epic, user_feedback, full_context, project_metadata)

        print(f"[StoryCrafter] Regenerated epic {regenerated_epic.get('id', 'unknown')}")
        return regenerated_epic

    async def regenerate_story(
        self,
        epic: Dict[str, Any],
        story: Dict[str, Any],
        user_feedback: str,
        consensus_messages: List[Dict[str, str]],
        project_metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        PUBLIC API: Regenerate a single story based on user feedback

        Args:
            epic: Parent epic object (for context)
            story: Original story object to regenerate
            user_feedback: User's comments on what needs to change
            consensus_messages: List of messages from 3-agent discussion
            project_metadata: Optional project metadata

        Returns:
            Regenerated story object
        """
        print(f"[StoryCrafter] Regenerating story: {story.get('id', 'unknown')}")

        full_context = self._format_full_consensus_for_prompt(consensus_messages, project_metadata)
        regenerated_story = await self._regenerate_single_story(epic, story, user_feedback, full_context, project_metadata)

        print(f"[StoryCrafter] Regenerated story {regenerated_story.get('id', 'unknown')}")
        return regenerated_story

    # ============================================================
    # STEP 1: EXTRACT REQUIREMENTS
    # ============================================================

    def _extract_requirements(
        self,
        messages: List[Dict[str, str]],
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Extract structured requirements from consensus messages

        Input: Raw messages from Alex, Blake, Casey
        Output: Structured requirements dict
        """
        requirements = {
            "project_name": "",
            "project_description": "",
            "target_users": "",
            "platform": "",
            "timeline": "",
            "team_size": "",
            "tech_stack": {},
            "mvp_features": [],
            "post_mvp_features": [],
            "constraints": [],
            "product_requirements": [],
            "technical_requirements": [],
            "project_requirements": []
        }

        # Extract from metadata if provided
        if metadata:
            requirements.update({
                k: v for k, v in metadata.items()
                if k in requirements
            })

        # Extract from messages
        for msg in messages:
            role = msg.get('role', '').lower()
            content = msg.get('content', '')

            if role == 'system':
                # Extract project name and description
                if 'project:' in content.lower():
                    requirements['project_name'] = self._extract_project_name(content)
                    requirements['project_description'] = content

            elif role == 'alex':  # Product Manager
                requirements['product_requirements'].append(content)
                # Extract MVP features
                if 'mvp' in content.lower() or 'core feature' in content.lower():
                    features = self._extract_features(content)
                    requirements['mvp_features'].extend(features)

            elif role == 'blake':  # Technical Architect
                requirements['technical_requirements'].append(content)
                # Extract tech stack
                tech_keywords = ['frontend', 'backend', 'database', 'framework', 'library']
                for keyword in tech_keywords:
                    if keyword in content.lower():
                        extracted = self._extract_tech_stack(content, keyword)
                        if extracted:
                            requirements['tech_stack'][keyword] = extracted

            elif role == 'casey':  # Project Manager
                requirements['project_requirements'].append(content)
                # Extract timeline and team
                if 'week' in content.lower() or 'month' in content.lower():
                    requirements['timeline'] = self._extract_timeline(content)
                if 'developer' in content.lower() or 'team' in content.lower():
                    requirements['team_size'] = self._extract_team_size(content)

        return requirements

    def _extract_project_name(self, content: str) -> str:
        """Extract project name from content"""
        patterns = [
            r'Project:\s*([^\n]+)',
            r'Project Name:\s*([^\n]+)',
            r'Building\s+(?:a|an)\s+([^\n]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return "Unnamed Project"

    def _extract_features(self, content: str) -> List[str]:
        """Extract features from content"""
        features = []
        # Look for bullet points or numbered lists
        lines = content.split('\n')
        for line in lines:
            if line.strip().startswith(('-', '*', '•')) or re.match(r'^\d+\.', line.strip()):
                feature = re.sub(r'^[-*•\d.]\s*', '', line.strip())
                if feature and len(feature) > 10:
                    features.append(feature)
        return features

    def _extract_tech_stack(self, content: str, keyword: str) -> str:
        """Extract technology for specific keyword"""
        # Simple extraction - look for common patterns
        patterns = [
            rf'{keyword}:\s*([^\n,]+)',
            rf'{keyword}\s+(?:using|with)\s+([^\n,]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return ""

    def _extract_timeline(self, content: str) -> str:
        """Extract timeline information"""
        # Look for patterns like "8 weeks", "3 months", "12-14 weeks"
        match = re.search(r'(\d+(?:-\d+)?)\s+(week|month)s?', content, re.IGNORECASE)
        if match:
            return match.group(0)
        return ""

    def _extract_team_size(self, content: str) -> str:
        """Extract team size information"""
        match = re.search(r'(\d+(?:-\d+)?)\s+(?:developer|dev)s?', content, re.IGNORECASE)
        if match:
            return match.group(0)
        return ""

    # ============================================================
    # STEP 2: GENERATE BACKLOG WITH CLAUDE (Legacy mode)
    # ============================================================

    async def _generate_backlog_with_claude(
        self,
        requirements: Dict[str, Any]
    ) -> str:
        """
        Generate backlog using Claude API with optimized prompt

        This is the core AI generation step (legacy mode)
        """
        prompt = self._build_claude_prompt(requirements)

        print(f"[StoryCrafter] Calling Claude API (model: {self.claude_model})...")

        message = self.anthropic_client.messages.create(
            model=self.claude_model,
            max_tokens=self.claude_max_tokens,
            temperature=self.temperature,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        # Extract text from Claude response
        response_text = message.content[0].text

        print(f"[StoryCrafter] ✅ Claude API response received ({len(response_text)} chars)")

        return response_text

    def _build_claude_prompt(self, requirements: Dict[str, Any]) -> str:
        """Build optimized prompt for Claude API (legacy mode)"""
        req_text = self._format_requirements_for_prompt(requirements)

        prompt = f"""You are an expert Agile Product Owner and Technical Architect with 15+ years of experience creating comprehensive project backlogs.

Your task is to generate a complete, production-ready backlog for the following project:

{req_text}

## GENERATION REQUIREMENTS

Generate a comprehensive backlog with:

1. **5-8 EPICS** covering all major functional areas
2. **20-40 USER STORIES** distributed across epics
3. **DETAILED ACCEPTANCE CRITERIA** for each story (4-7 criteria per story)
   - Use Given-When-Then format where applicable
   - Make criteria specific, testable, and measurable
   - Include both functional and non-functional requirements
   - Cover edge cases and error scenarios
4. **TECHNICAL TASKS** for each story (3-6 specific implementation tasks)
5. **MVP PRIORITIZATION** based on timeline

## OUTPUT FORMAT

Respond with VALID JSON ONLY. No markdown, no explanation, just the JSON.

Generate the backlog now:"""

        return prompt

    def _format_requirements_for_prompt(self, req: Dict[str, Any]) -> str:
        """Format requirements dict into readable prompt text"""
        parts = []

        # Project basics
        if req.get('project_name'):
            parts.append(f"**PROJECT**: {req['project_name']}")

        if req.get('project_description'):
            parts.append(f"**DESCRIPTION**: {req['project_description']}")

        # Features
        if req.get('mvp_features'):
            features_text = '\n'.join([f"- {f}" for f in req['mvp_features']])
            parts.append(f"**MVP FEATURES**:\n{features_text}")

        return '\n\n'.join(parts)

    # ============================================================
    # STEP 2.5: GENERATE WITH FULL CONTEXT (NEW APPROACH)
    # ============================================================

    async def _generate_with_full_context(
        self,
        consensus_messages: List[Dict[str, str]],
        project_metadata: Dict[str, Any] = None
    ) -> str:
        """
        Generate backlog by passing full consensus directly to Claude
        Uses TWO-PHASE approach to overcome token limits:
        Phase 1: Generate epic structure (6-8 epics)
        Phase 2: Expand each epic with detailed stories (3-6 per epic)
        """

        # Format full context for prompt
        full_context = self._format_full_consensus_for_prompt(consensus_messages, project_metadata)

        # PHASE 1: Generate Epic Structure
        print("[StoryCrafter] Phase 1: Generating epic structure...")
        epics_list = await self._generate_epic_structure(full_context, project_metadata)

        # PHASE 2: Expand Each Epic with Stories
        print(f"[StoryCrafter] Phase 2: Expanding {len(epics_list)} epics with stories...")
        expanded_backlog = await self._expand_epics_with_stories(epics_list, full_context, project_metadata)

        return expanded_backlog

    def _format_full_consensus_for_prompt(
        self,
        messages: List[Dict[str, str]],
        metadata: Dict[str, Any] = None
    ) -> str:
        """
        Format full consensus messages for direct Claude prompt
        Preserves maximum context from VISHKAR discussion
        """
        parts = []

        # Add project metadata if available
        if metadata:
            parts.append("### PROJECT OVERVIEW")
            parts.append(f"**Name**: {metadata.get('project_name', 'N/A')}")
            parts.append(f"**Description**: {metadata.get('project_description', 'N/A')}")
            parts.append("")

        # Add full consensus messages
        parts.append("### 3-AGENT CONSENSUS DISCUSSION")
        parts.append("")

        for msg in messages:
            role = msg.get('role', 'unknown').upper()
            content = msg.get('content', '')

            parts.append(f"## {role}")
            parts.append(content)
            parts.append("")

        return '\n'.join(parts)

    async def _generate_epic_structure(
        self,
        full_context: str,
        project_metadata: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """Phase 1: Generate just the epic structure (6-8 epics)"""

        prompt = f"""You are an expert Agile Product Owner creating a comprehensive project backlog.

Your task: Generate a complete EPIC STRUCTURE for the project described below.

## REQUIREMENTS

Generate 6-8 EPICS covering ALL project areas:

1. **Authentication & User Management**
2. **Core Feature Set**
3. **Data Management & Offline**
4. **UI/UX & Frontend**
5. **Backend Infrastructure**
6. **Testing & QA**
7. **Deployment & DevOps**
8. **Additional Features**

{full_context}

## OUTPUT FORMAT

Return JSON array of epics ONLY. No stories yet.

[
  {{
    "id": "EPIC-1",
    "title": "Epic Title",
    "description": "Detailed epic description (2-3 sentences)",
    "priority": "High|Medium|Low",
    "category": "MVP|Post-MVP|Technical",
    "story_count_target": 4
  }}
]

Generate 6-8 epics covering all areas. JSON only, no markdown:"""

        message = self.anthropic_client.messages.create(
            model=self.claude_model,
            max_tokens=4096,
            temperature=self.temperature,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = message.content[0].text
        print(f"[StoryCrafter] Phase 1 complete: {len(response_text)} chars")

        # Parse JSON
        response_text = response_text.strip()
        if response_text.startswith('```'):
            response_text = response_text.split('```')[1]
            if response_text.startswith('json'):
                response_text = response_text[4:]
        response_text = response_text.strip()

        epics = json.loads(response_text)
        print(f"[StoryCrafter] Generated {len(epics)} epics")
        return epics

    async def _expand_epics_with_stories(
        self,
        epics_list: List[Dict[str, Any]],
        full_context: str,
        project_metadata: Dict[str, Any] = None
    ) -> str:
        """
        Phase 2: For each epic, generate 3-6 detailed stories
        Returns complete backlog JSON string
        """

        all_stories_by_epic = {}

        for i, epic in enumerate(epics_list, 1):
            print(f"[StoryCrafter]   Expanding {epic['id']}: {epic['title']}...")

            stories = await self._generate_stories_for_epic(epic, full_context, project_metadata)
            all_stories_by_epic[epic['id']] = stories

            print(f"[StoryCrafter]   Generated {len(stories)} stories for {epic['id']}")

        # Assemble final backlog
        final_backlog = {
            "project": {
                "name": project_metadata.get('project_name', 'Project') if project_metadata else 'Project',
                "description": project_metadata.get('project_description', '') if project_metadata else '',
                "target_users": project_metadata.get('target_users', '') if project_metadata else '',
                "platform": project_metadata.get('platform', '') if project_metadata else ''
            },
            "epics": []
        }

        for epic in epics_list:
            epic_with_stories = dict(epic)
            epic_with_stories['stories'] = all_stories_by_epic.get(epic['id'], [])
            # Remove temporary field
            epic_with_stories.pop('story_count_target', None)
            final_backlog['epics'].append(epic_with_stories)

        return json.dumps(final_backlog, indent=2)

    async def _generate_stories_for_epic(
        self,
        epic: Dict[str, Any],
        full_context: str,
        project_metadata: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate 3-6 detailed stories for a single epic
        Uses Claude (Anthropic) as primary, falls back to GPT-5 if needed
        """
        # Use Claude as primary for story generation
        return await self._generate_stories_for_epic_claude(epic, full_context, project_metadata)

    async def _generate_stories_for_epic_gpt5(
        self,
        epic: Dict[str, Any],
        full_context: str,
        project_metadata: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        DEPRECATED: Generate 3-6 detailed stories for a single epic using GPT-5
        Now using Claude as primary method
        """

        target_count = epic.get('story_count_target', 4)

        system_prompt = """You are an expert Agile Product Owner and Technical Architect with 15+ years of experience.
You create comprehensive, production-ready user stories with detailed acceptance criteria and technical implementation tasks."""

        user_prompt = f"""Generate {target_count} DETAILED USER STORIES for this epic:

## EPIC DETAILS
**ID**: {epic['id']}
**Title**: {epic['title']}
**Description**: {epic['description']}

## FULL PROJECT CONTEXT
{full_context}

## OUTPUT FORMAT

Return a JSON array of stories. CRITICAL: Output ONLY valid JSON, no markdown:

[
  {{
    "id": "{epic['id']}-1",
    "title": "Concise Story Title",
    "description": "As a [persona], I want [goal], so that [benefit]",
    "acceptance_criteria": [
      "GIVEN [precondition] WHEN [action] THEN [expected result]",
      "System validates [specific condition] and displays [specific feedback]",
      "User can successfully [specific action] within [time/performance constraint]",
      "[Edge case]: System handles [error scenario] by [expected behavior]",
      "[Non-functional]: [Performance/security/usability requirement met]"
    ],
    "technical_tasks": ["Task 1", "Task 2", "Task 3", "Task 4", "Task 5"],
    "priority": "P0",
    "story_points": 5,
    "estimated_hours": 10,
    "dependencies": [],
    "tags": ["mvp", "backend", "frontend"],
    "layer": "fullstack"
  }}
]

Generate exactly {target_count} stories. Output JSON only:"""

        # Use GPT-5 with massive context window
        response = self.openai_client.chat.completions.create(
            model=self.gpt_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_completion_tokens=self.gpt_max_tokens,
            response_format={"type": "json_object"}
        )

        response_text = response.choices[0].message.content.strip()

        # Parse JSON
        try:
            data = json.loads(response_text)

            # Handle if GPT wraps stories in an object
            if isinstance(data, dict) and 'stories' in data:
                stories = data['stories']
            elif isinstance(data, list):
                stories = data
            else:
                # Fallback: look for array in response
                if '[' in response_text:
                    start = response_text.find('[')
                    end = response_text.rfind(']')
                    array_text = response_text[start:end+1]
                    stories = json.loads(array_text)
                else:
                    raise ValueError("Could not find story array in GPT-5 response")

        except json.JSONDecodeError as e:
            print(f"[StoryCrafter] ❌ Failed to parse GPT-5 response as JSON: {e}")
            # This method is deprecated - should not be called anymore
            raise ValueError(f"GPT-5 story generation failed: {e}")

        return stories

    async def _generate_stories_for_epic_claude(
        self,
        epic: Dict[str, Any],
        full_context: str,
        project_metadata: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """Fallback method: Generate stories using Claude if GPT-5 fails"""
        target_count = epic.get('story_count_target', 4)

        prompt = f"""Generate {target_count} user stories for epic: {epic['title']}

Context: {full_context[:2000]}

Return JSON array only."""

        message = self.anthropic_client.messages.create(
            model=self.claude_model,
            max_tokens=4096,
            temperature=self.temperature,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = message.content[0].text.strip()

        # Clean JSON
        if response_text.startswith('```'):
            response_text = response_text.split('```')[1]
            if response_text.startswith('json'):
                response_text = response_text[4:]
        response_text = response_text.strip()

        stories = json.loads(response_text)
        return stories

    # ============================================================
    # ACCEPTANCE CRITERIA VALIDATION
    # ============================================================

    def _validate_acceptance_criteria(
        self,
        acceptance_criteria: List[str],
        story_id: str = "unknown"
    ) -> Dict[str, Any]:
        """
        Validate acceptance criteria for quality and completeness

        Args:
            acceptance_criteria: List of acceptance criteria strings
            story_id: Story identifier for logging

        Returns:
            Dictionary with validation results
        """
        validation = {
            "is_valid": True,
            "warnings": [],
            "quality_score": 0,
            "total_criteria": len(acceptance_criteria)
        }

        if not acceptance_criteria or len(acceptance_criteria) < 4:
            validation["is_valid"] = False
            validation["warnings"].append(f"Story {story_id}: Less than 4 acceptance criteria (found {len(acceptance_criteria)})")

        if len(acceptance_criteria) > 10:
            validation["warnings"].append(f"Story {story_id}: More than 10 criteria may be too granular (found {len(acceptance_criteria)})")

        # Check for quality indicators
        quality_indicators = {
            "has_given_when_then": False,
            "has_edge_cases": False,
            "has_non_functional": False,
            "has_specific_validation": False
        }

        for criterion in acceptance_criteria:
            criterion_lower = criterion.lower()

            # Check for Given-When-Then format
            if "given" in criterion_lower and "when" in criterion_lower and "then" in criterion_lower:
                quality_indicators["has_given_when_then"] = True

            # Check for edge cases
            if "edge case" in criterion_lower or "error" in criterion_lower or "failure" in criterion_lower:
                quality_indicators["has_edge_cases"] = True

            # Check for non-functional requirements
            if any(term in criterion_lower for term in ["performance", "security", "usability", "accessibility", "non-functional"]):
                quality_indicators["has_non_functional"] = True

            # Check for specific validation
            if "validate" in criterion_lower or "verify" in criterion_lower:
                quality_indicators["has_specific_validation"] = True

        # Calculate quality score
        validation["quality_score"] = sum(quality_indicators.values())
        validation["quality_indicators"] = quality_indicators

        # Add recommendation if quality is low
        if validation["quality_score"] < 2:
            validation["warnings"].append(
                f"Story {story_id}: Low quality score ({validation['quality_score']}/4). "
                "Consider adding Given-When-Then format, edge cases, or non-functional requirements."
            )

        return validation

    def _validate_backlog_acceptance_criteria(self, backlog: Dict[str, Any]) -> None:
        """
        Validate acceptance criteria for all stories in backlog

        Args:
            backlog: Parsed backlog dictionary

        Logs warnings for stories with low-quality acceptance criteria
        """
        print("[StoryCrafter] Validating acceptance criteria quality...")

        total_stories = 0
        stories_with_warnings = 0
        all_warnings = []

        for epic in backlog.get('epics', []):
            for story in epic.get('stories', []):
                total_stories += 1
                story_id = story.get('id', 'unknown')
                acceptance_criteria = story.get('acceptance_criteria', [])

                validation = self._validate_acceptance_criteria(acceptance_criteria, story_id)

                if validation['warnings']:
                    stories_with_warnings += 1
                    all_warnings.extend(validation['warnings'])

        # Log summary
        if all_warnings:
            print(f"[StoryCrafter] ⚠️  Acceptance Criteria Validation: {stories_with_warnings}/{total_stories} stories have quality warnings")
            for warning in all_warnings[:5]:  # Show first 5 warnings
                print(f"[StoryCrafter]   - {warning}")
            if len(all_warnings) > 5:
                print(f"[StoryCrafter]   ... and {len(all_warnings) - 5} more warnings")
        else:
            print(f"[StoryCrafter] ✅ All {total_stories} stories have quality acceptance criteria")

    # ============================================================
    # STEP 3: PARSE AND VALIDATE
    # ============================================================

    def _parse_and_validate(self, raw_json_str: str) -> Dict[str, Any]:
        """Parse and validate JSON backlog"""
        # Clean up markdown code blocks if present
        cleaned = raw_json_str.strip()
        if cleaned.startswith('```'):
            cleaned = cleaned.split('```')[1]
            if cleaned.startswith('json'):
                cleaned = cleaned[4:]
        cleaned = cleaned.strip()

        # Parse JSON
        try:
            backlog = json.loads(cleaned)
        except json.JSONDecodeError as e:
            print(f"[StoryCrafter] ❌ JSON parse error: {e}")
            raise ValueError(f"Failed to parse backlog JSON: {e}")

        # Basic validation
        if 'epics' not in backlog:
            raise ValueError("Backlog missing 'epics' field")

        if not isinstance(backlog['epics'], list):
            raise ValueError("'epics' must be a list")

        print(f"[StoryCrafter] Parsed {len(backlog['epics'])} epics")

        return backlog

    # ============================================================
    # STEP 4: TRANSFORM TO VISHKAR FORMAT
    # ============================================================

    def _transform_to_vishkar_format(
        self,
        parsed_backlog: Dict[str, Any],
        requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Transform parsed backlog to VISHKAR frontend format"""

        total_stories = sum(len(epic.get('stories', [])) for epic in parsed_backlog.get('epics', []))
        total_hours = sum(
            sum(story.get('estimated_hours', 0) for story in epic.get('stories', []))
            for epic in parsed_backlog.get('epics', [])
        )

        vishkar_format = {
            "project": parsed_backlog.get('project', {}),
            "metadata": {
                "total_epics": len(parsed_backlog.get('epics', [])),
                "total_stories": total_stories,
                "total_estimated_hours": total_hours,
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "generator": "StoryCrafter v2.0 (Anthropic + OpenAI)"
            },
            "epics": parsed_backlog.get('epics', [])
        }

        return vishkar_format

    # ============================================================
    # REGENERATION METHODS
    # ============================================================

    async def _regenerate_single_epic(
        self,
        epic: Dict[str, Any],
        user_feedback: str,
        full_context: str,
        project_metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Regenerate a single epic based on user feedback using Claude Sonnet 4.5

        Args:
            epic: Original epic object to regenerate
            user_feedback: User's comments on what needs to change
            full_context: Full project context
            project_metadata: Project metadata

        Returns:
            Regenerated epic object
        """

        prompt = f"""You are an expert Agile Product Owner creating project epics.

## ORIGINAL EPIC

**ID**: {epic['id']}
**Title**: {epic['title']}
**Description**: {epic['description']}
**Priority**: {epic.get('priority', 'Medium')}
**Category**: {epic.get('category', 'MVP')}

## USER FEEDBACK

The user has provided the following feedback on this epic:

{user_feedback}

## PROJECT CONTEXT

{full_context}

## TASK

Based on the user feedback, generate an IMPROVED VERSION of this epic.

The regenerated epic should:
1. Address all points raised in the user feedback
2. Maintain the same ID: {epic['id']}
3. Keep the same general scope unless feedback suggests otherwise
4. Have an improved title and description
5. Maintain consistency with the project context

## OUTPUT FORMAT

Return a JSON object for the regenerated epic:

{{
  "id": "{epic['id']}",
  "title": "Improved Epic Title",
  "description": "Enhanced epic description (2-3 sentences)",
  "priority": "High|Medium|Low",
  "category": "MVP|Post-MVP|Technical",
  "story_count_target": 4,
  "regeneration_notes": "Brief note on what was changed based on feedback"
}}

Generate JSON only, no markdown:"""

        message = self.anthropic_client.messages.create(
            model=self.claude_model,
            max_tokens=2048,
            temperature=self.temperature,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = message.content[0].text.strip()

        # Clean JSON
        if response_text.startswith('```'):
            response_text = response_text.split('```')[1]
            if response_text.startswith('json'):
                response_text = response_text[4:]
        response_text = response_text.strip()

        regenerated_epic = json.loads(response_text)
        print(f"[StoryCrafter] Regenerated epic {epic['id']}")

        return regenerated_epic

    async def _regenerate_single_story(
        self,
        epic: Dict[str, Any],
        story: Dict[str, Any],
        user_feedback: str,
        full_context: str,
        project_metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Regenerate a single story based on user feedback
        Uses Claude (Anthropic) as primary method

        Args:
            epic: Parent epic object (for context)
            story: Original story object to regenerate
            user_feedback: User's comments on what needs to change
            full_context: Full project context
            project_metadata: Project metadata

        Returns:
            Regenerated story object with improved acceptance criteria and tasks
        """
        # Use Claude as primary for story regeneration
        return await self._regenerate_single_story_claude(epic, story, user_feedback, full_context, project_metadata)

    async def _regenerate_single_story_gpt5(
        self,
        epic: Dict[str, Any],
        story: Dict[str, Any],
        user_feedback: str,
        full_context: str,
        project_metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        DEPRECATED: Regenerate a single story based on user feedback using GPT-5
        Now using Claude as primary method

        Args:
            epic: Parent epic object (for context)
            story: Original story object to regenerate
            user_feedback: User's comments on what needs to change
            full_context: Full project context
            project_metadata: Project metadata

        Returns:
            Regenerated story object with improved acceptance criteria and tasks
        """

        system_prompt = """You are an expert Agile Product Owner and Technical Architect with 15+ years of experience.
You create comprehensive, production-ready user stories with detailed acceptance criteria and technical implementation tasks.
Your stories are clear, actionable, and follow industry best practices."""

        user_prompt = f"""Regenerate a USER STORY based on user feedback.

## PARENT EPIC

**ID**: {epic['id']}
**Title**: {epic['title']}
**Description**: {epic['description']}

## ORIGINAL STORY

**ID**: {story['id']}
**Title**: {story['title']}
**Description**: {story.get('description', '')}
**Priority**: {story.get('priority', 'P1')}
**Story Points**: {story.get('story_points', 0)}
**Estimated Hours**: {story.get('estimated_hours', 0)}

**Current Acceptance Criteria**:
{json.dumps(story.get('acceptance_criteria', []), indent=2)}

**Current Technical Tasks**:
{json.dumps(story.get('technical_tasks', []), indent=2)}

## USER FEEDBACK

The user has provided the following feedback on this story:

{user_feedback}

## PROJECT CONTEXT

{full_context[:2000]}

## TASK

Generate an IMPROVED VERSION of this story that addresses the user feedback.

The regenerated story should:
1. Address all points raised in the user feedback
2. Maintain the same ID: {story['id']}
3. Follow proper format: "As a [persona], I want [goal], so that [benefit]"
4. Include 5-7 DETAILED acceptance criteria using:
   - Given-When-Then format where applicable
   - Specific, testable, and measurable conditions
   - Edge cases and error scenarios
   - Non-functional requirements (performance, security, usability)
5. List 4-7 detailed technical implementation tasks
6. Assign realistic story points (2, 3, 5, or 8)
7. Estimate hours appropriately
8. Identify dependencies if applicable
9. Add relevant tags (mvp, backend, frontend, etc.)
10. Specify layer (fullstack, backend, frontend, database, or infrastructure)

## OUTPUT FORMAT

Return a JSON object for the regenerated story. CRITICAL: Output ONLY valid JSON, no markdown:

{{
  "id": "{story['id']}",
  "title": "Improved Story Title",
  "description": "As a [persona], I want [goal], so that [benefit]",
  "acceptance_criteria": [
    "GIVEN [precondition] WHEN [action] THEN [expected result]",
    "System validates [specific condition] and provides [specific feedback]",
    "User can successfully [specific action] within [performance constraint]",
    "[Edge case]: System handles [error scenario] by [expected behavior]",
    "[Non-functional]: [Performance/security/usability requirement met]",
    "Additional detailed testable criterion 6"
  ],
  "technical_tasks": [
    "Improved implementation task 1",
    "Improved implementation task 2",
    "Improved implementation task 3",
    "Improved implementation task 4",
    "Improved implementation task 5",
    "Testing task 6"
  ],
  "priority": "P0",
  "story_points": 5,
  "estimated_hours": 10,
  "dependencies": [],
  "tags": ["mvp", "backend", "frontend"],
  "layer": "fullstack",
  "regeneration_notes": "Brief note on what was changed based on feedback"
}}

Generate JSON only, no markdown code blocks:"""

        # Use GPT-5 for detailed story regeneration
        response = self.openai_client.chat.completions.create(
            model=self.gpt_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_completion_tokens=8192,  # More tokens for detailed story
            response_format={"type": "json_object"}  # Force JSON response
        )

        response_text = response.choices[0].message.content.strip()

        # Parse JSON
        try:
            regenerated_story = json.loads(response_text)
        except json.JSONDecodeError as e:
            print(f"[StoryCrafter] ❌ Failed to parse GPT-5 response: {e}")
            # Fallback to Claude if GPT-5 fails
            print(f"[StoryCrafter] Falling back to Claude for story {story['id']}")
            return await self._regenerate_single_story_claude(epic, story, user_feedback, full_context, project_metadata)

        print(f"[StoryCrafter] Regenerated story {story['id']}")

        return regenerated_story

    async def _regenerate_single_story_claude(
        self,
        epic: Dict[str, Any],
        story: Dict[str, Any],
        user_feedback: str,
        full_context: str,
        project_metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Fallback: Regenerate story using Claude if GPT-5 fails
        """

        prompt = f"""You are an expert Agile Product Owner creating user stories.

## PARENT EPIC: {epic['title']}
{epic['description']}

## ORIGINAL STORY

ID: {story['id']}
Title: {story['title']}
Description: {story.get('description', '')}

## USER FEEDBACK

{user_feedback}

## PROJECT CONTEXT

{full_context[:1500]}

## TASK

Generate an IMPROVED VERSION addressing the feedback.

Include:
- "As a [persona], I want [goal], so that [benefit]" format
- 5-7 DETAILED acceptance criteria (use Given-When-Then format, include edge cases, non-functional requirements)
- 4-7 detailed technical tasks
- Realistic story points and hours

## OUTPUT FORMAT

JSON object:

{{
  "id": "{story['id']}",
  "title": "Improved Title",
  "description": "As a [persona], I want [goal], so that [benefit]",
  "acceptance_criteria": [
    "GIVEN [precondition] WHEN [action] THEN [expected result]",
    "System validates [specific condition] and provides [specific feedback]",
    "User can [specific action] within [performance constraint]",
    "[Edge case]: System handles [error scenario] by [expected behavior]",
    "[Non-functional]: [Performance/security/usability requirement]",
    "Additional detailed testable criterion"
  ],
  "technical_tasks": ["Task 1", "Task 2", "Task 3", "Task 4", "Task 5"],
  "priority": "P0",
  "story_points": 5,
  "estimated_hours": 10,
  "dependencies": [],
  "tags": ["mvp", "backend"],
  "layer": "fullstack",
  "regeneration_notes": "Changes made based on feedback"
}}

JSON only:"""

        message = self.anthropic_client.messages.create(
            model=self.claude_model,
            max_tokens=4096,
            temperature=self.temperature,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = message.content[0].text.strip()

        # Clean JSON
        if response_text.startswith('```'):
            response_text = response_text.split('```')[1]
            if response_text.startswith('json'):
                response_text = response_text[4:]
        response_text = response_text.strip()

        regenerated_story = json.loads(response_text)
        return regenerated_story


# ============================================================
# SINGLETON INSTANCE
# ============================================================

_story_crafter_instance = None

def get_storycrafter_service(anthropic_api_key: str = None, openai_api_key: str = None):
    """Get singleton instance of StoryCrafter service"""
    global _story_crafter_instance

    if _story_crafter_instance is None:
        _story_crafter_instance = VISHKARStoryCrafterService(anthropic_api_key, openai_api_key)

    return _story_crafter_instance
