#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
Command discovery for SlashSense.

Scans ~/.claude/plugins/ and extracts ALL slash commands
from all installed plugins.
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any
import re


def discover_plugins_dir() -> Path:
    """Find the Claude plugins directory."""
    claude_home = Path.home() / ".claude"
    plugins_dir = claude_home / "plugins"
    
    if not plugins_dir.exists():
        return None
    
    return plugins_dir


def extract_command_from_md(md_file: Path) -> Dict[str, str]:
    """
    Extract command name and description from markdown file.
    
    Expected format:
    ---
    name: command-name
    description: Command description
    ---
    """
    try:
        content = md_file.read_text()
        
        # Extract frontmatter
        match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not match:
            return None
        
        frontmatter = match.group(1)
        
        # Parse YAML-like frontmatter
        name = None
        description = None
        
        for line in frontmatter.split('\n'):
            if line.startswith('name:'):
                name = line.split(':', 1)[1].strip()
            elif line.startswith('description:'):
                description = line.split(':', 1)[1].strip()
        
        if name:
            return {
                'command': name,
                'description': description or 'No description',
                'plugin': md_file.parent.parent.name,
                'file': str(md_file)
            }
    except Exception as e:
        return None
    
    return None


def discover_all_commands() -> List[Dict[str, Any]]:
    """
    Discover all slash commands from installed plugins.
    
    Returns:
        List of command metadata dicts
    """
    plugins_dir = discover_plugins_dir()
    if not plugins_dir:
        return []
    
    commands = []
    
    # Scan each plugin directory
    for plugin_dir in plugins_dir.iterdir():
        if not plugin_dir.is_dir():
            continue
        
        # Check for commands directory
        commands_dir = plugin_dir / "commands"
        if not commands_dir.exists():
            continue
        
        # Extract commands from .md files
        for md_file in commands_dir.glob("*.md"):
            cmd_info = extract_command_from_md(md_file)
            if cmd_info:
                commands.append(cmd_info)
    
    return commands


def save_discovered_commands(commands: List[Dict[str, Any]], output_file: Path):
    """Save discovered commands to JSON file."""
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(json.dumps(commands, indent=2))


if __name__ == "__main__":
    commands = discover_all_commands()
    
    print(f"Discovered {len(commands)} commands:")
    for cmd in commands:
        print(f"  /{cmd['command']} - {cmd['description']}")
    
    # Save to data directory
    data_dir = Path(__file__).parent.parent / "data"
    save_discovered_commands(commands, data_dir / "discovered_commands.json")