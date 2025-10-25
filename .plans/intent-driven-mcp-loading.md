# Intent-Driven On-Demand MCP Loading for SlashSense

**Date:** 2025-10-16
**Status:** Planning
**Priority:** High

## Problem Statement

The user sought to optimize Claude Code's context window usage by preventing MCP (Model Context Protocol) servers from auto-loading at session start. While MCP servers provide valuable capabilities (browser automation, documentation lookup, web search, advanced reasoning), they consume significant context tokens (50k-85k tokens each) even when idle. The initial approach of using `enabledMcpjsonServers: []` only applied to project-level `.mcp.json` files, not user-level configurations in `.claude.json`.

Through experimentation and research, the user discovered that:
1. MCP servers configured at user-level auto-load regardless of settings
2. Community tools exist (McPick, MCP Server Manager) that move servers between `mcpServers` and `_disabled_mcpServers` sections
3. The user's actual usage pattern involves explicitly telling Claude which MCP to use for specific tasks
4. An intent-driven approach would better match real-world workflow

**Core Insight:** The user doesn't need all MCPs available at session start; they need the right MCPs loaded based on task intent, configured automatically at the project level.

## Solution Architecture

### High-Level Flow

```
User Prompt
  → SlashSense Intent Detection
  → MCP Registry Match
  → Auto-configure Project .mcp.json
  → Claude loads only needed MCPs
  → Task execution with minimal context overhead
```

### Why This Approach is Superior

1. **Zero Context Waste** - No MCPs loaded until actually needed
2. **Intent Alignment** - User already signals intent ("use playwright", "search the web", "get docs for X")
3. **Infrastructure Reuse** - SlashSense already performs intent detection + prompt augmentation
4. **Project-Scoped** - Each project gets only relevant MCPs for its domain
5. **Automatic Cleanup** - Can remove MCPs when session ends or task completes
6. **Transparent** - Claude receives clear notification of available tools

## Implementation Plan

### Phase 1: MCP Registry System

#### 1.1 Local Registry Structure

Create `~/.claude/slashsense/mcp_registry.json`:

```json
{
  "version": "1.0.0",
  "mcps": {
    "sequential-thinking": {
      "triggers": [
        "think deeply",
        "analyze step by step",
        "reason through",
        "complex problem",
        "break down"
      ],
      "config": {
        "command": "/opt/homebrew/opt/node@22/bin/npx",
        "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"],
        "env": {}
      },
      "description": "Advanced reasoning for complex problems",
      "contextCost": "~1.5k tokens",
      "tags": ["reasoning", "analysis"]
    },
    "context7": {
      "triggers": [
        "docs for",
        "documentation",
        "library docs",
        "api reference",
        "how to use"
      ],
      "config": {
        "command": "/opt/homebrew/opt/node@22/bin/npx",
        "args": ["-y", "@upstash/context7-mcp"],
        "env": {}
      },
      "description": "Library documentation lookup",
      "contextCost": "~2k tokens",
      "tags": ["documentation", "reference"]
    },
    "playwright": {
      "triggers": [
        "playwright",
        "browser test",
        "e2e test",
        "ui test",
        "automation",
        "screenshot"
      ],
      "config": {
        "command": "/opt/homebrew/opt/node@22/bin/npx",
        "args": ["-y", "@playwright/mcp"],
        "env": {}
      },
      "description": "Browser automation and testing",
      "contextCost": "~4k tokens",
      "tags": ["testing", "browser", "automation"]
    },
    "web": {
      "triggers": [
        "search web",
        "browse",
        "find online",
        "look up",
        "research"
      ],
      "config": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-brave-search"],
        "env": {
          "BRAVE_API_KEY": "${BRAVE_API_KEY}"
        }
      },
      "description": "Web search via Brave",
      "contextCost": "~2k tokens",
      "tags": ["web", "search", "research"]
    },
    "supabase": {
      "triggers": [
        "supabase",
        "database",
        "postgres",
        "query db",
        "sql"
      ],
      "config": {
        "command": "npx",
        "args": [
          "-y",
          "@supabase/mcp-server-supabase@latest",
          "--access-token",
          "${SUPABASE_ACCESS_TOKEN}"
        ],
        "env": {}
      },
      "description": "Supabase database integration",
      "contextCost": "~3k tokens",
      "tags": ["database", "backend", "postgres"]
    },
    "filesystem": {
      "triggers": [
        "read files in",
        "access directory",
        "file operations on",
        "scan folder"
      ],
      "config": {
        "command": "npx",
        "args": [
          "-y",
          "@modelcontextprotocol/server-filesystem",
          "${TARGET_PATH}"
        ],
        "env": {}
      },
      "description": "File system access for specific directories",
      "contextCost": "~2k tokens",
      "tags": ["filesystem", "files"],
      "requiresVariable": "TARGET_PATH"
    }
  }
}
```

#### 1.2 Registry Management Commands

Add to SlashSense:
- `/mcp-registry list` - Show all available MCPs
- `/mcp-registry add <name> <config>` - Add custom MCP to registry
- `/mcp-registry remove <name>` - Remove from registry
- `/mcp-registry update` - Sync with official MCP Registry API

### Phase 2: Intent Detection Enhancement

#### 2.1 MCP Trigger Matching

Enhance SlashSense intent detector (`unified_intent_detector.py`):

```python
def detect_required_mcps(user_prompt: str, registry: dict) -> list[str]:
    """
    Detect which MCPs are needed based on user prompt triggers.

    Args:
        user_prompt: The user's input text
        registry: The MCP registry dictionary

    Returns:
        List of MCP names that should be activated
    """
    detected_mcps = []
    prompt_lower = user_prompt.lower()

    for mcp_name, mcp_config in registry["mcps"].items():
        # Check if any trigger phrase is in the prompt
        for trigger in mcp_config["triggers"]:
            if trigger in prompt_lower:
                detected_mcps.append(mcp_name)
                break

    return detected_mcps
```

#### 2.2 Variable Resolution

Handle MCPs that require runtime variables (like filesystem paths):

```python
def resolve_mcp_variables(mcp_config: dict, context: dict) -> dict:
    """
    Replace variable placeholders in MCP config with actual values.

    Args:
        mcp_config: The MCP configuration
        context: Dictionary of available variables

    Returns:
        Config with resolved variables
    """
    resolved = copy.deepcopy(mcp_config)

    # Replace in args
    for i, arg in enumerate(resolved["args"]):
        if "${" in arg:
            var_name = arg.replace("${", "").replace("}", "")
            if var_name in context:
                resolved["args"][i] = context[var_name]

    # Replace in env
    for key, value in resolved["env"].items():
        if "${" in value:
            var_name = value.replace("${", "").replace("}", "")
            if var_name in context:
                resolved["env"][key] = context[var_name]

    return resolved
```

### Phase 3: Project .mcp.json Auto-Configuration

#### 3.1 Setup Script

Create SlashSense helper to modify project `.mcp.json`:

```python
import json
import os
from pathlib import Path

def setup_project_mcps(
    project_root: str,
    mcp_names: list[str],
    registry: dict,
    variables: dict = None
) -> None:
    """
    Configure project-level .mcp.json with required MCP servers.

    Args:
        project_root: Path to project directory
        mcp_names: List of MCP names to configure
        registry: MCP registry dictionary
        variables: Optional runtime variables for MCP configs
    """
    mcp_json_path = Path(project_root) / ".mcp.json"

    # Load existing config or create new
    if mcp_json_path.exists():
        with open(mcp_json_path, 'r') as f:
            config = json.load(f)
    else:
        config = {"mcpServers": {}}

    # Add requested MCPs
    for mcp_name in mcp_names:
        if mcp_name not in registry["mcps"]:
            continue

        mcp_config = registry["mcps"][mcp_name]["config"]

        # Resolve variables if needed
        if variables and registry["mcps"][mcp_name].get("requiresVariable"):
            mcp_config = resolve_mcp_variables(mcp_config, variables)

        # Add to config
        config["mcpServers"][mcp_name] = mcp_config

    # Write back to file
    with open(mcp_json_path, 'w') as f:
        json.dump(config, f, indent=2)

    # Add to .gitignore if contains secrets
    if any(registry["mcps"][name]["config"]["env"] for name in mcp_names):
        gitignore_path = Path(project_root) / ".gitignore"
        if gitignore_path.exists():
            with open(gitignore_path, 'a') as f:
                f.write("\n# MCP servers with secrets\n.mcp.json\n")
```

#### 3.2 Cleanup Strategy

Option 1: Session-end cleanup
```python
def cleanup_session_mcps(project_root: str) -> None:
    """Remove project MCPs at session end."""
    mcp_json_path = Path(project_root) / ".mcp.json"
    if mcp_json_path.exists():
        mcp_json_path.unlink()
```

Option 2: Keep for session continuity
- Leave `.mcp.json` in place for multi-session projects
- User can manually delete or use `/mcp-cleanup` command

### Phase 4: Prompt Augmentation

#### 4.1 SlashSense Output Format

When MCPs are detected and configured:

```markdown
[SlashSense Analysis]

**Detected Intent:** Browser Testing + Documentation Lookup
**Configured MCPs:** playwright, context7

These MCP servers have been added to your project's .mcp.json:
- @playwright - Browser automation and E2E testing (~4k tokens)
- @context7 - Library documentation lookup (~2k tokens)

You can reference these servers using @mentions in your prompts.

**Augmented Prompt:**
[Original user prompt with slash command enhancements]
```

#### 4.2 Claude Instructions

Include in system prompt augmentation:

```
The following MCP servers are now available for this task:
- playwright: Use for browser automation, screenshots, and E2E testing
- context7: Use for fetching library documentation and API references

To use an MCP server, reference it with @ notation (e.g., @playwright).
```

### Phase 5: Official MCP Registry Integration

#### 5.1 API Structure

The official MCP Registry provides a REST API at:
```
https://registry.modelcontextprotocol.io/v0/servers
```

**Response Structure:**
```json
{
  "servers": [
    {
      "server": {
        "$schema": "https://static.modelcontextprotocol.io/schemas/2025-09-29/server.schema.json",
        "name": "ai.aliengiraffe/spotdb",
        "description": "Ephemeral data sandbox for AI workflows",
        "repository": {
          "url": "https://github.com/aliengiraffe/spotdb",
          "source": "github"
        },
        "version": "0.1.0",
        "packages": [
          {
            "registryType": "oci",
            "identifier": "docker.io/aliengiraffe/spotdb:0.1.0",
            "transport": {"type": "stdio"},
            "environmentVariables": [...]
          }
        ]
      },
      "_meta": {
        "io.modelcontextprotocol.registry/official": {
          "status": "active",
          "publishedAt": "2025-10-09T17:05:17.793149Z",
          "updatedAt": "2025-10-09T17:05:17.793149Z",
          "isLatest": true
        }
      }
    }
  ],
  "metadata": {
    "nextCursor": "ai.explorium/mcp-explorium:1.0.0",
    "count": 3
  }
}
```

**Query Parameters:**
- `limit` - Number of results (pagination)
- `search` - Search term
- `cursor` - Pagination cursor from previous response

#### 5.2 Registry Sync Feature

Implement periodic sync to discover new MCPs:

```python
import requests

def sync_official_registry(local_registry_path: str) -> dict:
    """
    Fetch servers from official MCP Registry and merge with local registry.

    Args:
        local_registry_path: Path to local mcp_registry.json

    Returns:
        Updated registry dictionary
    """
    # Load local registry
    with open(local_registry_path, 'r') as f:
        local_registry = json.load(f)

    # Fetch from official registry
    official_servers = []
    cursor = None

    while True:
        url = "https://registry.modelcontextprotocol.io/v0/servers?limit=100"
        if cursor:
            url += f"&cursor={cursor}"

        response = requests.get(url)
        data = response.json()

        official_servers.extend(data["servers"])

        cursor = data["metadata"].get("nextCursor")
        if not cursor:
            break

    # Convert official format to SlashSense format
    for server_data in official_servers:
        server = server_data["server"]
        name = server["name"].replace("/", "_")  # Normalize name

        # Skip if already in local registry
        if name in local_registry["mcps"]:
            continue

        # Extract NPM package if available
        npm_package = None
        for package in server.get("packages", []):
            if package.get("registryType") == "npm":
                npm_package = package["identifier"]
                break

        if not npm_package:
            continue

        # Add to registry with minimal config
        local_registry["mcps"][name] = {
            "triggers": [],  # User must configure
            "config": {
                "command": "npx",
                "args": ["-y", npm_package],
                "env": {}
            },
            "description": server["description"],
            "source": "official-registry",
            "repository": server.get("repository", {}).get("url", "")
        }

    # Save updated registry
    with open(local_registry_path, 'w') as f:
        json.dump(local_registry, f, indent=2)

    return local_registry
```

#### 5.3 Discovery UI

Add SlashSense command to browse official registry:

```bash
/mcp-discover [search-term]
```

Output:
```
Found 12 MCP servers matching "database":

1. Supabase MCP (@supabase/mcp-server-supabase)
   ✓ Already in your registry
   Description: PostgreSQL database access via Supabase

2. Turso Cloud (turso-cloud)
   ⊕ Add to registry
   Description: SQLite database access via Turso

3. MongoDB MCP (mongodb/mcp-server)
   ⊕ Add to registry
   Description: MongoDB database operations

Use '/mcp-registry add <name>' to add a server to your registry.
```

### Phase 6: Advanced Features

#### 6.1 Smart Trigger Learning

Track which MCPs are manually requested and auto-add trigger phrases:

```python
def learn_trigger_from_usage(prompt: str, used_mcp: str, registry: dict) -> None:
    """
    Extract key phrases from prompts where user explicitly requested an MCP.
    Add them as triggers if not already present.
    """
    # Extract potential trigger phrases (using simple word extraction)
    # In production, use more sophisticated NLP

    words = prompt.lower().split()
    bigrams = [" ".join(words[i:i+2]) for i in range(len(words)-1)]

    current_triggers = set(registry["mcps"][used_mcp]["triggers"])

    for bigram in bigrams:
        # If this bigram appears frequently with this MCP, add it
        if bigram not in current_triggers and is_relevant_trigger(bigram, used_mcp):
            registry["mcps"][used_mcp]["triggers"].append(bigram)
```

#### 6.2 Context Budget Management

Monitor total context usage and warn when MCPs would exceed budget:

```python
def check_context_budget(mcp_names: list[str], registry: dict, max_tokens: int = 30000) -> tuple[bool, int]:
    """
    Verify that requested MCPs fit within context budget.

    Returns:
        (fits_in_budget, total_cost)
    """
    total_cost = 0
    for name in mcp_names:
        cost_str = registry["mcps"][name].get("contextCost", "0k tokens")
        cost = int(cost_str.replace("~", "").replace("k tokens", "")) * 1000
        total_cost += cost

    return (total_cost <= max_tokens, total_cost)
```

#### 6.3 Project MCP Profiles

Save common MCP combinations as profiles:

```json
{
  "profiles": {
    "web-dev": ["playwright", "web", "context7"],
    "backend-dev": ["supabase", "web"],
    "testing": ["playwright", "sequential-thinking"],
    "research": ["web", "context7", "sequential-thinking"]
  }
}
```

Usage:
```
/mcp-profile web-dev
```

## Benefits Summary

1. **Massive Context Savings**
   - Before: 8 MCPs × 50k tokens = 400k tokens at session start
   - After: 0-3 MCPs × 50k tokens = 0-150k tokens, loaded on-demand

2. **Better User Experience**
   - No manual MCP management required
   - Intent naturally signals needed tools
   - Transparent activation process

3. **Project Optimization**
   - Web projects get web tools
   - Backend projects get database tools
   - Testing projects get automation tools

4. **Extensibility**
   - Easy to add new MCPs to registry
   - Can sync with official MCP Registry
   - Supports custom/private MCPs

5. **SlashSense Integration**
   - Leverages existing intent detection
   - Fits naturally into prompt augmentation flow
   - Enhances core value proposition

## Implementation Timeline

**Week 1: Foundation**
- Create MCP registry structure
- Implement basic trigger matching
- Build .mcp.json configuration logic

**Week 2: Integration**
- Integrate with SlashSense intent detector
- Add prompt augmentation
- Test with real projects

**Week 3: Polish**
- Implement official registry sync
- Add management commands
- Write documentation

**Week 4: Advanced Features**
- Smart trigger learning
- Context budget management
- Project profiles

## Success Metrics

- Context token reduction: Target 60%+ reduction in average session context usage
- Auto-detection accuracy: 85%+ correct MCP suggestions
- User satisfaction: Reduces manual MCP configuration to zero
- Coverage: Supports 95% of common use cases without manual intervention

## Future Enhancements

1. **Multi-project MCP caching** - Share loaded MCPs across related projects
2. **Predictive loading** - Pre-load likely MCPs based on project analysis
3. **Usage analytics** - Track which MCPs are most valuable per project type
4. **Community trigger sharing** - Crowdsource trigger phrases for better detection
5. **Cost-aware optimization** - Balance capability vs context cost per task

## References

- [GitHub Issue #4879](https://github.com/anthropics/claude-code/issues/4879) - MCP Enable/Disable Toggle
- [GitHub Issue #6638](https://github.com/anthropics/claude-code/issues/6638) - Dynamic MCP Loading
- [Official MCP Registry](https://registry.modelcontextprotocol.io)
- [MCP Registry API Docs](https://registry.modelcontextprotocol.io/docs)
- Claude Code Documentation: [MCP Guide](https://docs.claude.com/en/docs/claude-code/mcp)

## Backup of Original User MCP Configuration

Stored at: `/tmp/mcp_servers_backup.json`

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/Users/shakes/Library/Mobile Documents/com~apple~CloudDocs/Projects/AI Engineering/aidoppel"],
      "env": {}
    },
    "web": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": {"BRAVE_API_KEY": "BSArn1BxHcmAyCnjzDsd6AHLweal5sM"}
    },
    "supabase": {
      "command": "npx",
      "args": ["-y", "@supabase/mcp-server-supabase@latest", "--access-token", "sbp_878d2969aeb84ba417a0bab28177ee66ddecc760"],
      "env": {}
    },
    "sequential-thinking": {
      "command": "/opt/homebrew/opt/node@22/bin/npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"],
      "env": {}
    },
    "context7": {
      "command": "/opt/homebrew/opt/node@22/bin/npx",
      "args": ["-y", "@upstash/context7-mcp"],
      "env": {}
    },
    "magic": {
      "command": "/opt/homebrew/opt/node@22/bin/npx",
      "args": ["-y", "@21st-dev/magic"],
      "env": {}
    },
    "playwright": {
      "command": "/opt/homebrew/opt/node@22/bin/npx",
      "args": ["-y", "@playwright/mcp"],
      "env": {}
    },
    "chrome-devtools": {
      "command": "/opt/homebrew/opt/node@22/bin/npx",
      "args": ["-y", "chrome-devtools-mcp@latest"],
      "env": {}
    }
  }
}
```

---

**Notes:**
- User-level MCPs have been removed from `.claude.json`
- `enabledMcpjsonServers: []` added to `~/.claude/settings.json` (though this only affects project-level configs)
- OpenTelemetry configured for observability at `http://localhost:4000`
- Custom hooks remain active for specialized tracking
