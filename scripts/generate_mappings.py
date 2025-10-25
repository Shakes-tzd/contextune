#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pyyaml>=6.0",
# ]
# ///

"""
Generate intent mappings from markdown frontmatter.

Scans commands/, skills/, and agents/ directories for .md files,
extracts frontmatter, and generates intent_mappings.json OR
provides data for direct loading by keyword_matcher.

This eliminates manual JSON maintenance - keywords live with docs!
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Any
import yaml


def extract_frontmatter(filepath: Path) -> Dict[str, Any]:
    """Extract YAML frontmatter from markdown file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Match YAML frontmatter between --- delimiters
        match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if not match:
            return {}

        frontmatter_text = match.group(1)
        return yaml.safe_load(frontmatter_text) or {}

    except Exception as e:
        print(f"Warning: Could not parse {filepath}: {e}", file=sys.stderr)
        return {}


def scan_commands(base_dir: Path) -> Dict[str, Dict[str, Any]]:
    """Scan commands/ directory for markdown files."""
    commands = {}
    commands_dir = base_dir / 'commands'

    if not commands_dir.exists():
        return commands

    for md_file in commands_dir.glob('*.md'):
        frontmatter = extract_frontmatter(md_file)

        if 'name' not in frontmatter:
            continue

        command_name = frontmatter['name']
        if not command_name.startswith('/'):
            command_name = f"/{command_name}"

        commands[command_name] = {
            'description': frontmatter.get('description', ''),
            'keywords': frontmatter.get('keywords', []),
            'category': frontmatter.get('category', 'General'),
            'file': str(md_file.relative_to(base_dir))
        }

    return commands


def scan_skills(base_dir: Path) -> Dict[str, Dict[str, Any]]:
    """Scan skills/*/SKILL.md files for skill definitions."""
    skills = {}
    skills_dir = base_dir / 'skills'

    if not skills_dir.exists():
        return skills

    for skill_file in skills_dir.glob('*/SKILL.md'):
        frontmatter = extract_frontmatter(skill_file)

        if 'name' not in frontmatter:
            continue

        skill_name = frontmatter['name']
        if not skill_name.startswith('skill:') and not skill_name.startswith('ctx:'):
            skill_name = f"skill:{skill_name}"

        skills[skill_name] = {
            'description': frontmatter.get('description', ''),
            'keywords': frontmatter.get('keywords', []),
            'allowed_tools': frontmatter.get('allowed-tools', []),
            'file': str(skill_file.relative_to(base_dir))
        }

    return skills


def scan_agents(base_dir: Path) -> Dict[str, Dict[str, Any]]:
    """Scan agents/*.md files for agent definitions."""
    agents = {}
    agents_dir = base_dir / 'agents'

    if not agents_dir.exists():
        return agents

    for agent_file in agents_dir.glob('*.md'):
        frontmatter = extract_frontmatter(agent_file)

        if 'name' not in frontmatter:
            continue

        agent_name = frontmatter['name']
        if not agent_name.startswith('agent:'):
            agent_name = f"agent:{agent_name}"

        agents[agent_name] = {
            'description': frontmatter.get('description', ''),
            'keywords': frontmatter.get('keywords', []),
            'subagent_type': frontmatter.get('subagent_type', ''),
            'file': str(agent_file.relative_to(base_dir))
        }

    return agents


def generate_mappings(base_dir: Path) -> Dict[str, Any]:
    """Generate complete intent mappings from all sources."""
    commands = scan_commands(base_dir)
    skills = scan_skills(base_dir)
    agents = scan_agents(base_dir)

    return {
        'metadata': {
            'version': '0.9.0',
            'generated': 'auto',
            'description': 'Auto-generated from markdown frontmatter',
            'total_commands': len(commands),
            'total_skills': len(skills),
            'total_agents': len(agents),
        },
        'commands': commands,
        'skills': skills,
        'agents': agents,
    }


def main():
    """Generate intent_mappings.json from markdown files."""
    base_dir = Path(__file__).parent.parent

    print("🔍 Scanning for commands, skills, and agents...")
    mappings = generate_mappings(base_dir)

    print(f"✅ Found:")
    print(f"   - {mappings['metadata']['total_commands']} commands")
    print(f"   - {mappings['metadata']['total_skills']} skills")
    print(f"   - {mappings['metadata']['total_agents']} agents")

    # Write to JSON
    output_path = base_dir / 'data' / 'intent_mappings.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(mappings, f, indent=2)

    print(f"\n✅ Generated: {output_path}")
    print("\n💡 Run this script during deployment to auto-sync mappings!")


if __name__ == '__main__':
    main()
