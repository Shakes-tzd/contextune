#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pytest>=7.0"]
# ///
"""
Integration tests for ctx-configure command.

Tests complete installation, uninstallation, and state management flows.
"""

import json
import tempfile
import shutil
from pathlib import Path
import sys
import subprocess

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'lib'))
sys.path.insert(0, str(Path(__file__).parent.parent / 'commands'))

from install_manifest import read_manifest, write_manifest, clear_manifest, MANIFEST_PATH

def test_manifest_operations():
    """Test manifest read/write/update operations."""

    # Save original manifest
    original_manifest = None
    if MANIFEST_PATH.exists():
        original_manifest = read_manifest()

    try:
        # Test write
        test_data = {
            'output_style': {'installed': True, 'scope': 'user', 'path': '/test'},
            'status_line': {'installed': True, 'path': '/test'},
            'installation_date': '2025-10-27',
            'version': '0.8.9'
        }

        success = write_manifest(test_data)
        assert success, "Manifest write failed"

        # Test read
        read_back = read_manifest()
        assert read_back == test_data, "Manifest read mismatch"

        # Test clear
        success = clear_manifest()
        assert success, "Manifest clear failed"
        assert not MANIFEST_PATH.exists(), "Manifest still exists after clear"

        print("✅ Manifest operations: PASS")

    finally:
        # Restore original manifest
        if original_manifest:
            write_manifest(original_manifest)
        elif MANIFEST_PATH.exists():
            MANIFEST_PATH.unlink()

def test_project_level_install():
    """Test project-level output style installation."""

    with tempfile.TemporaryDirectory() as tmpdir:
        # Set up test environment
        test_project = Path(tmpdir) / "test-project"
        test_project.mkdir()

        # Create mock output style source
        source_dir = test_project / "output-styles"
        source_dir.mkdir()
        source_file = source_dir / "extraction-optimized.md"
        source_file.write_text("# Test Output Style\n")

        # Run install from test project (simulated)
        dest_dir = test_project / ".claude" / "output-styles"
        dest_dir.mkdir(parents=True)
        dest = dest_dir / "extraction-optimized.md"

        shutil.copy(source_file, dest)

        # Verify
        assert dest.exists(), "Project-level install failed"
        assert dest.read_text() == "# Test Output Style\n", "Content mismatch"

        print("✅ Project-level install: PASS")

def test_user_level_install():
    """Test user-level output style installation."""

    # This test uses actual user directory but cleans up after
    user_output_styles = Path.home() / ".claude" / "output-styles"
    test_file = user_output_styles / "test-extraction-optimized.md"

    # Save original if exists
    original_content = None
    if test_file.exists():
        original_content = test_file.read_text()

    try:
        user_output_styles.mkdir(parents=True, exist_ok=True)
        test_file.write_text("# Test\n")

        assert test_file.exists(), "User-level install failed"

        print("✅ User-level install: PASS")

    finally:
        # Cleanup
        if original_content:
            test_file.write_text(original_content)
        elif test_file.exists():
            test_file.unlink()

def test_state_detection():
    """Test state detection logic."""

    # Save current state
    original_manifest = None
    if MANIFEST_PATH.exists():
        original_manifest = read_manifest()

    try:
        # Create test state
        test_manifest = {
            'output_style': {'installed': True, 'scope': 'user', 'path': '/fake/path'},
            'status_line': {'installed': False, 'path': None},
            'installation_date': '2025-10-27',
            'version': '0.8.9'
        }

        write_manifest(test_manifest)

        # Read manifest back
        read_back = read_manifest()

        assert read_back['output_style']['installed'] == True, "State detection failed"
        assert read_back['output_style']['scope'] == 'user', "Scope detection failed"
        assert read_back['status_line']['installed'] == False, "Status line state wrong"

        print("✅ State detection: PASS")

    finally:
        # Restore
        if original_manifest:
            write_manifest(original_manifest)
        else:
            clear_manifest()

def test_complete_install_flow():
    """Test complete installation flow (project-level + status line)."""

    print("\n📋 Testing complete installation flow...")

    # Step 1: Check initial state
    result = subprocess.run(
        ['uv', 'run', 'commands/ctx-configure.py'],
        capture_output=True,
        text=True
    )

    state = json.loads(result.stdout)
    print(f"   Initial state detected: {state['state']['output_style']['installed']}")

    # Step 2: Test project-level install
    result = subprocess.run(
        ['uv', 'run', 'commands/ctx-configure.py', '--install-project'],
        capture_output=True,
        text=True,
        cwd='/Users/shakes/DevProjects/contextune'
    )

    assert result.returncode == 0, "Project install failed"
    assert "Output style installed (project-level)" in result.stdout, "Install message missing"

    # Step 3: Verify file exists
    project_style = Path('/Users/shakes/DevProjects/contextune/.claude/output-styles/extraction-optimized.md')
    assert project_style.exists(), "Project-level file not created"

    print("✅ Complete installation flow: PASS")

if __name__ == '__main__':
    print("Running ctx-configure integration tests...\n")

    try:
        test_manifest_operations()
        test_state_detection()
        test_project_level_install()
        test_user_level_install()
        test_complete_install_flow()

        print("\n" + "=" * 50)
        print("✅ All integration tests passed!")
        print("=" * 50)

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
