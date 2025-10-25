# Contextune Skills

Contextune includes plugin-local skills that are automatically discovered and available when the plugin is installed.

## Skills Directory Structure

```
contextune/
└── skills/
    ├── software-architect/                  ✅ v0.8.0 (migrated, optimized)
    ├── researcher/                          ✅ v0.8.0 (new)
    ├── intent-recognition/                  ✅ Existing
    ├── parallel-development-expert/         ✅ Existing
    ├── performance-optimizer/               ✅ Existing
    └── git-worktree-master/                 ✅ Existing
```

## Included Skills

### 1. sc:architect (Migrated & Optimized in v0.8.0)

**Triggers:** "design", "architect", "break down", "best approach", "should I build"

**What it does:**
- Systematic architecture analysis workflow
- 5-step process: Understand → Research → Specify → Decompose → Plan
- WebSearch for existing solutions
- Build vs. Buy decision framework
- Task decomposition with dependency mapping
- Executable plans with phases

**Optimizations (v0.8.0):**
- 27% context reduction (226 → 166 lines)
- Retained all essential workflow steps
- Directive, concise phrasing
- Removed verbose examples

**Example:**
```
User: "design a caching layer for the app"
→ Skill activates
→ Follows: Understand → Research → Specify → Decompose → Plan
→ Returns: Architecture spec, researched alternatives, phased execution plan
```

**Location:** `skills/software-architect/SKILL.md`

---

### 2. ctx:researcher (NEW in v0.8.0)

**Triggers:** "research", "investigate", "find information about", "compare", "what's the best"

**What it does:**
- Executes `/ctx:research` command automatically
- Spawns 3 parallel Haiku agents:
  1. Web search for similar solutions
  2. Web search for libraries/tools
  3. Codebase pattern analysis
- Returns structured findings in 1-2 minutes (~$0.07)

**Example:**
```
User: "research best React state management libraries"
→ Skill activates
→ Runs: /ctx:research best React state management libraries 2025
→ Returns: Comprehensive comparison with pros/cons, recommendations
```

**Location:** `skills/researcher/SKILL.md`

---

### 2. contextune:intent-recognition

**Triggers:** "what can Contextune do?", "how do I use this?", "show me examples"

**What it does:**
- Explains Contextune capabilities
- Shows available commands with examples
- Guides users through features
- Provides use case examples

**Location:** `skills/intent-recognition/SKILL.md`

---

### 3. contextune:parallel-development-expert

**Triggers:** "parallel work", "concurrent development", "work on multiple features"

**What it does:**
- Guides parallel development workflows
- Explains git worktree setup
- Task decomposition strategies
- Worktree management best practices

**Location:** `skills/parallel-development-expert/SKILL.md`

---

### 4. contextune:performance-optimizer

**Triggers:** "slow performance", "optimize", "bottlenecks", "benchmark"

**What it does:**
- Analyzes parallel workflow performance
- Identifies bottlenecks
- Calculates speedup metrics (Amdahl's Law)
- Provides optimization recommendations

**Location:** `skills/performance-optimizer/SKILL.md`

---

### 5. contextune:git-worktree-master

**Triggers:** "worktree issues", "stuck worktrees", "locked files", "cleanup worktrees"

**What it does:**
- Troubleshoots git worktree problems
- Handles worktree cleanup
- Resolves lock file issues
- Manages worktree lifecycle

**Location:** `skills/git-worktree-master/SKILL.md`

---

## Skill Invocation (v0.8.0)

### Automatic (via Prompt Augmentation)

When Contextune detects a command with a mapped skill:

```python
# User types: "research best Python async libraries"
↓
# Contextune detects: /ctx:research (95% keyword)
↓
# Hook augments prompt:
"research best Python async libraries. You can use your contextune:researcher skill to conduct this search."
↓
# Claude invokes contextune:researcher skill → Executes reliably!
```

### Manual Invocation

Users can also invoke skills manually:

```
Use your contextune:researcher skill to find the best database for my use case.
```

---

## Adding New Skills

### 1. Create Skill Directory

```bash
mkdir -p skills/my-new-skill
```

### 2. Create SKILL.md with Frontmatter

```markdown
---
name: contextune:my-new-skill
description: Brief description of what this skill does and when to use it.
---

# My New Skill

[Detailed documentation]

## When to Activate

[Triggers and conditions]

## Workflow

[Step-by-step process]
```

### 3. Skills are Auto-Discovered

No need to register in plugin.json - Claude Code automatically discovers skills from `skills/*/SKILL.md`.

### 4. Map to Command (Optional)

If you want prompt augmentation, add to `hooks/user_prompt_submit.py`:

```python
SKILL_MAPPING = {
    "/my:command": "contextune:my-new-skill",
}
```

---

## Skill Naming Convention

**Match slash command namespace for consistency:**

| Command | Skill Name | Rationale |
|---------|-----------|-----------|
| `/ctx:research` | `ctx:researcher` | Contextune namespace |
| `/ctx:plan` | `ctx:planner` | Contextune namespace |
| `/sc:design` | `sc:architect` | SuperClaude namespace |
| `/sc:analyze` | `sc:analyzer` | SuperClaude namespace |

**Benefit:** Clear, consistent mapping - users can intuitively know:
- `/ctx:*` commands → `ctx:*` skills (Contextune)
- `/sc:*` commands → `sc:*` skills (SuperClaude)

**Plugin-provided skills (Contextune-specific):**
```
name: contextune:intent-recognition
name: contextune:parallel-development-expert
```

These don't map to slash commands, so they use the `contextune:` prefix for namespacing.

---

## Skill Frontmatter Fields

```yaml
---
name: contextune:skill-name        # Required: Unique identifier
description: Brief description...  # Required: Triggers and usage
allowed-tools:                      # Optional: Restrict tool access
  - Bash
  - Read
  - Write
---
```

---

## Benefits of Plugin-Local Skills

✅ **Version controlled** - Distributed with plugin
✅ **Automatically available** - Users get them when installing plugin
✅ **Consistent experience** - Same behavior across all users
✅ **Easy updates** - Update plugin → skills updated
✅ **No manual installation** - Zero setup for users

---

## Future Skills (Planned)

### v0.9.0
- **contextune:code-analyzer** - Wraps `/sc:analyze`
- **contextune:parallel-planner** - Wraps `/ctx:plan`
- **contextune:code-improver** - Wraps `/sc:improve`

### v1.0.0
- **contextune:test-runner** - Wraps `/sc:test`
- **contextune:documentation-generator** - Wraps `/sc:document`

---

## Testing Skills Locally

```bash
# Install plugin locally
cd /path/to/contextune
git tag v0.8.0  # Tag current version

# In Claude Code
/plugin install contextune@local

# Test skill
Type: "research best Go web frameworks"
→ Should invoke contextune:researcher skill
→ Executes /ctx:research command
→ Returns findings
```

---

## Debugging Skills

### Check if Skill is Discovered

```bash
# List available skills (from Claude Code)
# Skills should appear in autocomplete when typing "use your"

# Or check plugin directory
ls -la ~/.claude/plugins/marketplaces/Contextune/skills/
```

### View Skill Contents

```bash
cat ~/.claude/plugins/marketplaces/Contextune/skills/researcher/SKILL.md
```

### Enable Debug Logging

See `hooks/user_prompt_submit.py` - already includes debug logging:
```
DEBUG: Augmenting prompt for Claude (detection #X)
```

---

## Related Documentation

- `docs/PROMPT_AUGMENTATION.md` - How skills are invoked automatically
- `CHANGELOG.md` - Version history
- `README.md` - Plugin overview

---

**Skills make Contextune commands more reliable by leveraging Claude's native Skill tool instead of text-based slash commands!**
