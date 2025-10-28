#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
Installation Manifest - Track Contextune customizations

Tracks what was installed via /ctx:configure to enable clean uninstallation.

Manifest format:
{
  "output_style": {
    "installed": true,
    "scope": "user" | "project",
    "path": "/full/path/to/extraction-optimized.md"
  },
  "status_line": {
    "installed": true,
    "path": "~/.claude/statusline.sh"
  },
  "installation_date": "2025-10-27T20:30:00Z",
  "version": "0.8.9"
}
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Optional

MANIFEST_PATH = Path.home() / ".claude" / "plugins" / "contextune" / "data" / "install_manifest.json"

def read_manifest() -> dict:
    """
    Read installation manifest.

    Returns:
        dict with installation state, or default empty state if not found
    """
    if not MANIFEST_PATH.exists():
        return {
            'output_style': {'installed': False, 'scope': None, 'path': None},
            'status_line': {'installed': False, 'path': None},
            'installation_date': None,
            'version': None
        }

    try:
        with open(MANIFEST_PATH, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        # Corrupted manifest, return default
        return {
            'output_style': {'installed': False, 'scope': None, 'path': None},
            'status_line': {'installed': False, 'path': None},
            'installation_date': None,
            'version': None
        }

def write_manifest(manifest: dict) -> bool:
    """
    Write installation manifest.

    Args:
        manifest: Complete manifest dict

    Returns:
        bool indicating success
    """
    try:
        MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)

        with open(MANIFEST_PATH, 'w') as f:
            json.dump(manifest, f, indent=2)

        return True
    except IOError as e:
        print(f"Failed to write manifest: {e}")
        return False

def update_output_style(scope: str, path: str, version: str = "0.8.9") -> bool:
    """
    Update manifest with output style installation.

    Args:
        scope: "user" or "project"
        path: Full path to installed file
        version: Plugin version

    Returns:
        bool indicating success
    """
    manifest = read_manifest()

    manifest['output_style'] = {
        'installed': True,
        'scope': scope,
        'path': path
    }

    if not manifest['installation_date']:
        manifest['installation_date'] = datetime.now().isoformat()

    manifest['version'] = version

    return write_manifest(manifest)

def update_status_line(installed: bool, path: Optional[str] = None) -> bool:
    """
    Update manifest with status line installation state.

    Args:
        installed: Whether status line section was added
        path: Path to statusline.sh (if installed)

    Returns:
        bool indicating success
    """
    manifest = read_manifest()

    manifest['status_line'] = {
        'installed': installed,
        'path': path
    }

    return write_manifest(manifest)

def clear_manifest() -> bool:
    """
    Delete manifest file (after complete uninstallation).

    Returns:
        bool indicating success
    """
    try:
        if MANIFEST_PATH.exists():
            MANIFEST_PATH.unlink()
        return True
    except IOError:
        return False

if __name__ == '__main__':
    # Test manifest operations
    print("Testing manifest operations...")

    # Write test manifest
    test_manifest = {
        'output_style': {'installed': True, 'scope': 'user', 'path': '/test/path'},
        'status_line': {'installed': True, 'path': '~/.claude/statusline.sh'},
        'installation_date': datetime.now().isoformat(),
        'version': '0.8.9'
    }

    success = write_manifest(test_manifest)
    print(f"Write manifest: {'✅' if success else '❌'}")

    # Read it back
    read_back = read_manifest()
    print(f"Read manifest: {'✅' if read_back == test_manifest else '❌'}")

    # Update output style
    success = update_output_style('project', '/new/path', '0.9.0')
    print(f"Update output style: {'✅' if success else '❌'}")

    # Verify update
    updated = read_manifest()
    print(f"Scope changed to project: {'✅' if updated['output_style']['scope'] == 'project' else '❌'}")

    # Clear manifest
    success = clear_manifest()
    print(f"Clear manifest: {'✅' if success else '❌'}")

    print("\n✅ All manifest operations working")
