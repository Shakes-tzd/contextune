"""
Shared Extraction Patterns for Conversation Transcripts

Used by:
- hooks/session_end_extractor.py
- scripts/decision-sync.py
- hooks/context_preserver.py

Extracts structured content from Claude Code conversation transcripts
using extraction-optimized output format patterns.
"""

import re
from typing import Optional, List, Dict, Any
import yaml


def extract_assistant_text(entry: dict) -> Optional[str]:
    """
    Extract text content from assistant message entry.

    Args:
        entry: Transcript entry dict

    Returns:
        Extracted text or None
    """
    if entry.get('type') != 'assistant':
        return None

    message = entry.get('message', {})
    if not isinstance(message, dict):
        return None

    content = message.get('content', [])

    # Handle both formats
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        return ' '.join(
            block.get('text', '')
            for block in content
            if block.get('type') == 'text'
        )

    return None


def extract_designs(transcript: List[dict]) -> List[dict]:
    """
    Find all design proposals in conversation.

    Detection patterns (from extraction-optimized style):
    - **Type:** Design
    - ## Architecture
    - ## Task Breakdown
    - Multiple YAML blocks

    Args:
        transcript: List of conversation entries

    Returns:
        List of design dicts with index, timestamp, content, pattern_count
    """
    designs = []

    for i, entry in enumerate(transcript):
        text = extract_assistant_text(entry)
        if not text:
            continue

        # Detect extraction-optimized design patterns
        patterns = [
            r"\*\*Type:\*\* Design",
            r"## Architecture",
            r"## Task Breakdown",
            r"```yaml\n.*?architecture:",
            r"```yaml\n.*?tasks:",
            r"\*\*Status:\*\* (Complete|Draft)",
            r"\*\*Estimated Tokens:\*\*",
        ]

        pattern_count = sum(
            len(re.findall(p, text, re.IGNORECASE | re.DOTALL)) for p in patterns
        )

        # Require at least 3 patterns for design detection
        if pattern_count >= 3:
            designs.append({
                'index': i,
                'timestamp': entry.get('timestamp', ''),
                'content': text,
                'pattern_count': pattern_count
            })

    return designs


def extract_decisions(transcript: List[dict]) -> List[dict]:
    """
    Find architectural decisions in conversation.

    Detection patterns:
    - ## Decision:
    - **Status:** Accepted|Proposed|Rejected
    - ### Alternatives Considered

    Args:
        transcript: List of conversation entries

    Returns:
        List of decision dicts with timestamp, content
    """
    decisions = []

    for entry in transcript:
        text = extract_assistant_text(entry)
        if not text:
            continue

        decision_patterns = [
            r"## Decision:",
            r"\*\*Status:\*\* (Accepted|Proposed|Rejected)",
            r"### Alternatives Considered",
            r"### Context",
            r"### Consequences",
        ]

        pattern_count = sum(
            len(re.findall(p, text, re.IGNORECASE)) for p in decision_patterns
        )

        if pattern_count >= 3:
            decisions.append({
                'timestamp': entry.get('timestamp', ''),
                'content': text
            })

    return decisions


def extract_research(transcript: List[dict]) -> List[dict]:
    """
    Find research findings in conversation.

    Detection patterns:
    - ## Research: [Topic]
    - ### Key Findings
    - YAML blocks with findings

    Args:
        transcript: List of conversation entries

    Returns:
        List of research dicts with topic, findings, timestamp
    """
    research_entries = []

    for entry in transcript:
        text = extract_assistant_text(entry)
        if not text:
            continue

        # Detect research pattern
        research_match = re.search(r'## Research:\s*(.+?)$', text, re.MULTILINE)
        if not research_match:
            continue

        topic = research_match.group(1).strip()

        # Extract findings YAML block
        findings_yaml = re.search(r'### Key Findings\n\n```yaml\n(.*?)```', text, re.DOTALL)
        findings = []

        if findings_yaml:
            try:
                findings_data = yaml.safe_load(findings_yaml.group(1))
                if isinstance(findings_data, dict) and 'findings' in findings_data:
                    findings = [f.get('finding', '') for f in findings_data['findings']]
            except yaml.YAMLError:
                pass

        # Extract recommendations
        recommendations = re.findall(r'###? Recommendations?\n\n(.+?)(?=\n##|\Z)', text, re.DOTALL)

        research_entries.append({
            'topic': topic,
            'findings': findings if findings else [f"Research about {topic}"],
            'recommendations': recommendations[0].strip() if recommendations else '',
            'timestamp': entry.get('timestamp', ''),
            'content_snippet': text[:500]
        })

    return research_entries


def extract_title(content: str) -> Optional[str]:
    """
    Extract title from markdown (# Title pattern).

    Args:
        content: Markdown content

    Returns:
        Title string or None
    """
    match = re.search(r"^#\s+(.+?)$", content, re.MULTILINE)
    return match.group(1).strip() if match else None


def extract_yaml_blocks(content: str) -> List[dict]:
    """
    Extract and parse YAML blocks from markdown.

    Args:
        content: Markdown content with ```yaml blocks

    Returns:
        List of parsed YAML dicts
    """
    yaml_blocks = re.findall(r"```yaml\n(.*?)```", content, re.DOTALL)
    parsed = []

    for block in yaml_blocks:
        try:
            data = yaml.safe_load(block)
            if data:
                parsed.append(data)
        except yaml.YAMLError:
            continue

    return parsed
