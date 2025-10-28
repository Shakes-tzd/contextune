#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
Enhanced Contextune Configuration

Interactive configuration management using AskUserQuestion tool.

Features:
- Dual-scope output style installation (user-level or project-level)
- Status line integration
- Installation manifest tracking
- Clean uninstallation with warnings
"""

import json
import shutil
from pathlib import Path
import sys
import os
import re

# Add lib to path for manifest import
sys.path.insert(0, str(Path(__file__).parent.parent / 'lib'))
from install_manifest import read_manifest, update_output_style, update_status_line, clear_manifest

def detect_state() -> dict:
    """
    Detect current installation state.

    Returns:
        dict with complete state information
    """
    # Check manifest first
    manifest = read_manifest()

    # Verify files still exist
    user_path = Path.home() / ".claude" / "output-styles" / "extraction-optimized.md"
    project_path = Path.cwd() / ".claude" / "output-styles" / "extraction-optimized.md"
    statusline_path = Path.home() / ".claude" / "statusline.sh"

    output_style_installed = False
    output_style_scope = None
    output_style_path = None

    if user_path.exists():
        output_style_installed = True
        output_style_scope = 'user'
        output_style_path = str(user_path)
    elif project_path.exists():
        output_style_installed = True
        output_style_scope = 'project'
        output_style_path = str(project_path)

    # Check status line
    status_line_installed = False
    if statusline_path.exists():
        try:
            content = statusline_path.read_text()
            if 'Contextune' in content or 'ctx:' in content:
                status_line_installed = True
        except IOError:
            pass

    return {
        'output_style': {
            'installed': output_style_installed,
            'scope': output_style_scope,
            'path': output_style_path
        },
        'status_line': {
            'installed': status_line_installed,
            'path': str(statusline_path) if statusline_path.exists() else None
        },
        'manifest': manifest
    }

def install_output_style(scope: str = 'user') -> tuple[bool, str]:
    """
    Install extraction-optimized output style.

    Args:
        scope: 'user' for ~/.claude/output-styles/ or 'project' for .claude/output-styles/

    Returns:
        (success: bool, installed_path: str)
    """
    try:
        # Find plugin root via CLAUDE_PLUGIN_ROOT env var
        plugin_root = os.environ.get('CLAUDE_PLUGIN_ROOT')
        if not plugin_root:
            plugin_root = Path(__file__).parent.parent
        else:
            plugin_root = Path(plugin_root)

        source = plugin_root / "output-styles" / "extraction-optimized.md"

        if not source.exists():
            print(f"❌ Source not found: {source}", file=sys.stderr)
            return False, ""

        # Determine destination based on scope
        if scope == 'user':
            dest_dir = Path.home() / ".claude" / "output-styles"
        else:  # project
            dest_dir = Path.cwd() / ".claude" / "output-styles"

        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / "extraction-optimized.md"

        # Copy file
        shutil.copy(source, dest)

        # Update manifest
        update_output_style(scope, str(dest))

        return True, str(dest)

    except Exception as e:
        print(f"❌ Installation failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return False, ""

def install_status_line() -> bool:
    """
    Add Contextune section to ~/.claude/statusline.sh.

    Returns:
        bool indicating success
    """
    try:
        statusline_path = Path.home() / ".claude" / "statusline.sh"

        # Create statusline.sh from template if doesn't exist
        if not statusline_path.exists():
            statusline_path.parent.mkdir(parents=True, exist_ok=True)

            # Basic template
            template = '''#!/bin/bash
# Claude Code Status Line

OUTPUT=""

# Section: Contextune Commands
if grep -q '"contextune.*true' ~/.claude/settings.json 2>/dev/null; then
    YELLOW="\\033[1;33m"
    RESET="\\033[0m"
    OUTPUT="${OUTPUT}${YELLOW}Contextune:${RESET} /ctx:research | /ctx:plan | /ctx:execute"
fi

echo -e "$OUTPUT"
'''
            statusline_path.write_text(template)
            statusline_path.chmod(0o755)

            # Update manifest
            update_status_line(True, str(statusline_path))

            return True

        # Read existing file
        content = statusline_path.read_text()

        # Check if Contextune already present
        if 'Contextune' in content or 'ctx:' in content:
            print("ℹ️  Contextune already in status line", file=sys.stderr)
            update_status_line(True, str(statusline_path))
            return True

        # Find the final echo line
        lines = content.split('\n')
        insert_index = -1

        for i in range(len(lines) - 1, -1, -1):
            if lines[i].strip().startswith('echo'):
                insert_index = i
                break

        if insert_index == -1:
            # No echo found, append at end
            insert_index = len(lines)

        # Create Contextune section
        contextune_section = [
            '',
            '# Section: Contextune Commands',
            'if grep -q \'"contextune.*true\' ~/.claude/settings.json 2>/dev/null; then',
            '    YELLOW="\\033[1;33m"',
            '    RESET="\\033[0m"',
            '    OUTPUT="${OUTPUT} | ${YELLOW}Contextune:${RESET} /ctx:research | /ctx:plan | /ctx:execute"',
            'fi',
            ''
        ]

        # Insert section before echo
        new_lines = lines[:insert_index] + contextune_section + lines[insert_index:]

        # Write back
        statusline_path.write_text('\n'.join(new_lines))

        # Update manifest
        update_status_line(True, str(statusline_path))

        return True

    except Exception as e:
        print(f"❌ Status line installation failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return False

def uninstall_output_style(manifest: dict) -> tuple[bool, int]:
    """
    Remove output style based on manifest.

    Args:
        manifest: Installation manifest

    Returns:
        (success: bool, files_removed: int)
    """
    try:
        removed = 0
        output_style = manifest.get('output_style', {})

        if output_style.get('installed'):
            path = output_style.get('path')
            if path and Path(path).exists():
                Path(path).unlink()
                removed += 1
                print(f"✅ Removed output style: {path}", file=sys.stderr)

        return True, removed

    except Exception as e:
        print(f"❌ Failed to remove output style: {e}", file=sys.stderr)
        return False, 0

def uninstall_status_line(manifest: dict) -> tuple[bool, bool]:
    """
    Remove Contextune section from status line.

    Args:
        manifest: Installation manifest

    Returns:
        (success: bool, removed: bool)
    """
    try:
        status_line = manifest.get('status_line', {})

        if not status_line.get('installed'):
            return True, False

        statusline_path = Path.home() / ".claude" / "statusline.sh"

        if not statusline_path.exists():
            return True, False

        # Read content
        content = statusline_path.read_text()

        # Remove Contextune section (from # Section: Contextune to fi)
        pattern = r'\n# Section: Contextune Commands\n.*?fi\n'
        new_content = re.sub(pattern, '', content, flags=re.DOTALL)

        if new_content != content:
            statusline_path.write_text(new_content)
            print(f"✅ Removed Contextune from status line", file=sys.stderr)
            return True, True

        return True, False

    except Exception as e:
        print(f"❌ Failed to remove status line section: {e}", file=sys.stderr)
        return False, False

def cleanup_plans_directories() -> int:
    """
    Find and remove .plans/ directories.

    Returns:
        Number of directories removed
    """
    try:
        search_paths = [
            Path.cwd(),
            Path.home() / "DevProjects",
            Path.home() / "Projects",
            Path.home() / "Code",
            Path.home() / "dev"
        ]

        plans_dirs = []
        for search_path in search_paths:
            if search_path.exists() and search_path.is_dir():
                for plans_dir in search_path.glob('**/.plans'):
                    # Limit depth
                    relative = plans_dir.relative_to(search_path) if plans_dir.is_relative_to(search_path) else plans_dir
                    if len(relative.parts) <= 4:
                        plans_dirs.append(plans_dir)

        removed = 0
        for plans_dir in plans_dirs:
            try:
                shutil.rmtree(plans_dir)
                removed += 1
                print(f"   Removed: {plans_dir}", file=sys.stderr)
            except Exception as e:
                print(f"   Failed to remove {plans_dir}: {e}", file=sys.stderr)

        return removed

    except Exception as e:
        print(f"❌ Cleanup failed: {e}", file=sys.stderr)
        return 0

def output_instructions_for_claude():
    """
    Output JSON instructions for Claude to use AskUserQuestion.
    """
    state = detect_state()

    instructions = {
        'state': state,
        'next_action': 'use_ask_user_question',
        'instructions': None
    }

    if not state['output_style']['installed']:
        # Not installed - offer to install
        instructions['instructions'] = {
            'action': 'prompt_install',
            'message': (
                'Output style not installed. Use AskUserQuestion tool:\n\n'
                'Question: "Would you like to install the extraction-optimized output style?"\n'
                'Header: "Setup"\n'
                'Options:\n'
                '1. Install (Enable automatic documentation extraction)\n'
                '2. Skip (Can install later with /ctx:configure)\n\n'
                'If Install selected: Ask about scope (next prompt)\n'
                'If Skip: Show how to run /ctx:configure later'
            ),
            'scope_prompt': (
                'Question: "Where should the output style be installed?"\n'
                'Header: "Scope"\n'
                'Options:\n'
                '1. This project - Install to .claude/output-styles/ (project-specific, git-trackable)\n'
                '2. All projects - Install to ~/.claude/output-styles/ (available everywhere)\n\n'
                'After scope selected: Ask about status line (next prompt)'
            ),
            'status_line_prompt': (
                'Question: "Would you like to add Contextune to your status bar?"\n'
                'Header: "Status Bar"\n'
                'Options:\n'
                '1. Yes (Show Contextune commands in status bar - zero tokens)\n'
                '2. No (Skip status bar integration)\n\n'
                'After selection: Execute installation with chosen options'
            )
        }
    else:
        # Already installed - offer management
        scope_text = "user-level" if state['output_style']['scope'] == 'user' else "project-level"
        instructions['instructions'] = {
            'action': 'prompt_manage',
            'current_state': {
                'output_style': f"Installed ({scope_text})",
                'status_line': "Installed" if state['status_line']['installed'] else "Not installed"
            },
            'message': (
                f'Current installation:\n'
                f'• Output style: {state["output_style"]["scope"]}-level\n'
                f'• Status line: {"✅" if state["status_line"]["installed"] else "❌"}\n\n'
                'Use AskUserQuestion tool:\n\n'
                'Question: "Manage Contextune configuration"\n'
                'Header: "Configure"\n'
                'Options:\n'
                '1. Activate style (Make extraction-optimized active now)\n'
                '2. Reinstall (Change scope: user ↔ project)\n'
                '3. Uninstall (Remove all customizations)\n'
                '4. Keep as-is (No changes)\n\n'
                'Based on selection, execute appropriate action'
            )
        }

    return instructions

def main():
    """Main entry point for configuration script."""

    # Check for command-line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1]

        if arg == '--install-user':
            success, path = install_output_style(scope='user')
            if success:
                print(f"\n✅ Output style installed (user-level)")
                print(f"   Location: {path}")
            else:
                print(f"\n❌ Installation failed")
            sys.exit(0 if success else 1)

        elif arg == '--install-project':
            success, path = install_output_style(scope='project')
            if success:
                print(f"\n✅ Output style installed (project-level)")
                print(f"   Location: {path}")
            else:
                print(f"\n❌ Installation failed")
            sys.exit(0 if success else 1)

        elif arg == '--install-statusline':
            success = install_status_line()
            if success:
                print(f"\n✅ Status line integration added")
                print(f"   Location: ~/.claude/statusline.sh")
            else:
                print(f"\n❌ Status line installation failed")
            sys.exit(0 if success else 1)

        elif arg == '--uninstall':
            manifest = read_manifest()

            print("\n🗑️  Uninstalling Contextune customizations...\n")

            # Remove output style
            success, removed = uninstall_output_style(manifest)
            if removed:
                print(f"✅ Removed output style")

            # Remove status line
            success, removed = uninstall_status_line(manifest)
            if removed:
                print(f"✅ Removed status line integration")

            # Clear manifest
            clear_manifest()

            print(f"\n✅ Uninstallation complete!")
            print(f"\n⚠️  IMPORTANT: You can now safely disable the plugin:")
            print(f"   /plugin disable contextune")
            print(f"\nTo reinstall later:")
            print(f"   /plugin enable contextune")
            print(f"   /ctx:configure")

            sys.exit(0)

        elif arg == '--uninstall-with-cleanup':
            manifest = read_manifest()

            print("\n🗑️  Uninstalling with cleanup...\n")

            # Remove output style
            uninstall_output_style(manifest)

            # Remove status line
            uninstall_status_line(manifest)

            # Clean .plans/
            print(f"\n🗑️  Cleaning .plans/ directories...")
            removed_count = cleanup_plans_directories()
            print(f"✅ Removed {removed_count} .plans/ directories")

            # Clear manifest
            clear_manifest()

            print(f"\n✅ Complete uninstallation finished!")
            print(f"\n⚠️  You can now safely disable the plugin:")
            print(f"   /plugin disable contextune")

            sys.exit(0)

    # No arguments - output instructions for Claude
    instructions = output_instructions_for_claude()
    print(json.dumps(instructions, indent=2))
    sys.exit(0)

if __name__ == '__main__':
    main()
