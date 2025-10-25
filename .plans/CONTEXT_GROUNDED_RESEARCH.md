# Context-Grounded Research Architecture

**Created:** 2025-10-21
**Problem:** Research agents lack current context (codebase, date, existing plans)
**Solution:** Context injection via hooks + grounded research protocols

---

## 🎯 The Problem: Ungrounded Research

### Current Issues

**Issue 1: Outdated Web Searches**
```
Research Agent: "Best practices for X in 2024"
Reality: It's 2025! Search results are outdated.
```

**Issue 2: Missing Codebase Context**
```
Research Agent: "How to implement authentication?"
Reality: We already have auth in src/auth/! Don't reinvent.
```

**Issue 3: Ignoring Existing Plans/Specs**
```
Research Agent: "Should we use REST or GraphQL?"
Reality: ARCHITECTURE.md already specifies REST!
```

**Issue 4: Missing Project Context**
```
Research Agent: "What's the tech stack?"
Reality: package.json shows TypeScript + React!
```

---

## ✅ The Solution: Context-Grounded Research

### Architecture Overview

```
┌────────────────────────────────────────────────────────┐
│ Context Injection (via Hook)                           │
├────────────────────────────────────────────────────────┤
│ UserPromptSubmit hook captures:                        │
│ • Current date from <env>                              │
│ • Working directory                                     │
│ • Git repo info                                         │
│ • Tech stack (from package.json, etc.)                 │
│ • Existing plans (.parallel/plans/)                    │
│ • Specifications (docs/specs/, ARCHITECTURE.md)        │
│                                                          │
│ Injects into prompt as "RESEARCH CONTEXT"              │
└────────────────────────────────────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────────────────────┐
│ Research Agents (with Context)                         │
├────────────────────────────────────────────────────────┤
│ Receive grounded context:                              │
│ • "Today is 2025-10-21" ← Use in web searches          │
│ • "Codebase: TypeScript + React" ← Search accordingly  │
│ • "Existing auth in src/auth/" ← Don't duplicate       │
│ • "Spec: Use REST API" ← Follow spec                   │
│                                                          │
│ Research is now GROUNDED in reality!                   │
└────────────────────────────────────────────────────────┘
```

---

## 🔧 Implementation: Context Hook

### New Hook: context-injector

**File:** `hooks/context_injector.py`

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pathlib",
# ]
# ///

"""
Context injection hook for grounded research.
Injects current date, codebase info, and existing specs into prompts.
"""

import sys
import json
import os
from pathlib import Path
from datetime import datetime

def get_current_context():
    """Extract current context from environment and codebase."""

    # Get current date from environment (Claude Code provides this)
    # Format: YYYY-MM-DD
    current_date = datetime.now().strftime("%Y-%m-%d")

    # Get working directory
    working_dir = os.getcwd()
    project_name = Path(working_dir).name

    # Detect tech stack
    tech_stack = detect_tech_stack(working_dir)

    # Find existing specifications
    specs = find_specifications(working_dir)

    # Find existing plans
    plans = find_recent_plans(working_dir)

    return {
        "date": current_date,
        "project": project_name,
        "working_dir": working_dir,
        "tech_stack": tech_stack,
        "specifications": specs,
        "recent_plans": plans
    }

def detect_tech_stack(working_dir: str) -> dict:
    """Detect tech stack from project files."""
    stack = {}

    # Check for package.json (Node.js/TypeScript)
    package_json = Path(working_dir) / "package.json"
    if package_json.exists():
        try:
            import json
            with open(package_json) as f:
                pkg = json.load(f)
                stack["language"] = "TypeScript/JavaScript"
                stack["runtime"] = "Node.js"

                # Extract key dependencies
                deps = pkg.get("dependencies", {})
                if "react" in deps:
                    stack["framework"] = "React"
                elif "vue" in deps:
                    stack["framework"] = "Vue"
                elif "svelte" in deps:
                    stack["framework"] = "Svelte"

                stack["dependencies"] = list(deps.keys())[:10]  # Top 10
        except:
            pass

    # Check for pyproject.toml (Python)
    pyproject = Path(working_dir) / "pyproject.toml"
    if pyproject.exists():
        stack["language"] = "Python"
        stack["package_manager"] = "UV/pip"

    # Check for go.mod (Go)
    gomod = Path(working_dir) / "go.mod"
    if gomod.exists():
        stack["language"] = "Go"

    # Check for Cargo.toml (Rust)
    cargo = Path(working_dir) / "Cargo.toml"
    if cargo.exists():
        stack["language"] = "Rust"

    return stack

def find_specifications(working_dir: str) -> list:
    """Find existing specification documents."""
    specs = []

    spec_locations = [
        "docs/specs/",
        "docs/ARCHITECTURE.md",
        "ARCHITECTURE.md",
        "README.md",
        "CONTRIBUTING.md",
        "docs/DESIGN.md",
    ]

    for location in spec_locations:
        path = Path(working_dir) / location
        if path.exists():
            if path.is_file():
                specs.append(str(path.relative_to(working_dir)))
            elif path.is_dir():
                # Add all markdown files in specs directory
                for spec_file in path.glob("*.md"):
                    specs.append(str(spec_file.relative_to(working_dir)))

    return specs

def find_recent_plans(working_dir: str) -> list:
    """Find recent development plans."""
    plans_dir = Path(working_dir) / ".parallel/plans"

    if not plans_dir.exists():
        return []

    # Find plans from last 30 days
    recent_plans = []
    now = datetime.now()

    for plan_file in plans_dir.glob("PLAN-*.md"):
        # Extract timestamp from filename (PLAN-YYYYMMDD-HHMMSS.md)
        try:
            timestamp_str = plan_file.stem.split("-", 1)[1]  # Remove "PLAN-"
            plan_date = datetime.strptime(timestamp_str.split("-")[0], "%Y%m%d")

            # If within last 30 days, include it
            if (now - plan_date).days <= 30:
                recent_plans.append({
                    "file": str(plan_file.relative_to(working_dir)),
                    "date": plan_date.strftime("%Y-%m-%d"),
                    "age_days": (now - plan_date).days
                })
        except:
            pass

    # Sort by date (newest first)
    recent_plans.sort(key=lambda x: x["age_days"])

    return recent_plans[:5]  # Return 5 most recent

def format_context_for_injection(context: dict) -> str:
    """Format context for injection into prompt."""

    lines = []
    lines.append("📋 RESEARCH CONTEXT (Use this information in your research!)")
    lines.append("")

    # Current date (CRITICAL for web searches)
    lines.append(f"**Current Date:** {context['date']}")
    lines.append("⚠️ IMPORTANT: When searching the web, use THIS date, not 2024!")
    lines.append(f"   Search for '{context['date'].split('-')[0]}' or 'latest' not '2024'")
    lines.append("")

    # Project info
    lines.append(f"**Project:** {context['project']}")
    lines.append(f"**Directory:** {context['working_dir']}")
    lines.append("")

    # Tech stack
    if context['tech_stack']:
        lines.append("**Tech Stack:**")
        for key, value in context['tech_stack'].items():
            if isinstance(value, list):
                lines.append(f"  • {key}: {', '.join(value[:5])}")
            else:
                lines.append(f"  • {key}: {value}")
        lines.append("")

    # Existing specifications
    if context['specifications']:
        lines.append("**Existing Specifications (READ THESE FIRST!):**")
        for spec in context['specifications']:
            lines.append(f"  • {spec}")
        lines.append("")
        lines.append("⚠️ Do NOT research what's already specified!")
        lines.append("   Read these docs to understand existing decisions.")
        lines.append("")

    # Recent plans
    if context['recent_plans']:
        lines.append("**Recent Development Plans:**")
        for plan in context['recent_plans']:
            lines.append(f"  • {plan['file']} ({plan['age_days']} days ago)")
        lines.append("")
        lines.append("⚠️ Check if similar work was already planned!")
        lines.append("")

    lines.append("---")
    lines.append("")

    return "\n".join(lines)

def inject_context(prompt: str) -> str:
    """Inject context into user prompt."""

    # Get current context
    context = get_current_context()

    # Format for injection
    context_block = format_context_for_injection(context)

    # Inject at start of prompt
    return f"{context_block}\n{prompt}"

# Main hook execution
if __name__ == "__main__":
    # Read prompt from stdin
    try:
        hook_input = json.loads(sys.stdin.read())
        prompt = hook_input.get("prompt", "")
    except:
        sys.exit(0)  # Fail silently if no input

    # Only inject context if prompt mentions research/plan/execute
    keywords = ["research", "plan", "parallel", "execute", "analyze", "design"]
    should_inject = any(keyword in prompt.lower() for keyword in keywords)

    if should_inject:
        # Inject context
        modified_prompt = inject_context(prompt)

        # Output modified prompt
        output = {
            "continue": True,
            "modifiedPrompt": modified_prompt,
            "suppressOutput": False
        }

        print(json.dumps(output))
        sys.exit(0)
    else:
        # Don't inject, continue normally
        sys.exit(0)
```

### Hook Configuration

**File:** `hooks/hooks.json`

```json
{
  "userPromptSubmit": [
    {
      "command": "uv run hooks/context_injector.py",
      "description": "Inject current context for grounded research",
      "continueOnError": true,
      "timeout": 1000
    },
    {
      "command": "uv run hooks/user_prompt_submit.py",
      "description": "SlashSense intent detection",
      "continueOnError": true,
      "timeout": 5000
    }
  ]
}
```

**Note:** Context injector runs FIRST, then intent detection.

---

## 🔬 Enhanced Research Agent Prompts

### Updated Research Agent Template

**With Context Grounding:**

```markdown
Research Agent Prompt:

📋 RESEARCH CONTEXT (injected by hook):
**Current Date:** 2025-10-21
⚠️ Use THIS date in searches, not 2024!

**Project:** slashsense
**Tech Stack:** Python 3.10+, UV package manager

**Existing Specifications:**
• docs/ARCHITECTURE.md
• README.md
• CLAUDE.md

⚠️ READ SPECS FIRST before researching!

**Recent Plans:**
• .parallel/plans/PLAN-20251021-155507.md (0 days ago)

---

Your Research Task: [research task here]

**IMPORTANT RULES:**

1. **Use Current Date in Web Searches**
   ❌ Bad: "best practices for X in 2024"
   ✅ Good: "best practices for X in 2025"
   ✅ Better: "best practices for X latest"

2. **Check Existing Specs FIRST**
   Before researching, read:
   • docs/ARCHITECTURE.md
   • README.md

   If spec already answers your question, USE IT!
   Don't research what's already decided.

3. **Search Codebase for Existing Patterns**
   Before recommending new patterns, check:
   • grep -r "similar_feature" .
   • Does this already exist?

   Reuse existing patterns, don't invent new ones.

4. **Consider Tech Stack**
   We're using: Python 3.10+, UV

   Don't recommend:
   ❌ Node.js libraries (wrong stack!)
   ❌ pip install (we use UV!)

   Recommend:
   ✅ Python libraries compatible with 3.10+
   ✅ uv add commands

5. **Reference Recent Plans**
   Check if similar work was planned:
   • .parallel/plans/PLAN-20251021-155507.md

   Don't duplicate recent work!

**Research and report back with grounded findings.**
```

---

## 📊 Context Grounding Benefits

### Before (Ungrounded)

```
Research Agent 1:
"Searching: best practices for authentication 2024"
Result: Outdated 2024 practices

Research Agent 2:
"Searching: how to implement user auth"
Result: Generic advice (ignores existing src/auth/)

Research Agent 3:
"Searching: REST vs GraphQL comparison"
Result: Recommends GraphQL (ignores ARCHITECTURE.md spec!)

Quality: Low (outdated, duplicative, ignores specs)
```

### After (Grounded)

```
Research Agent 1:
"Searching: best practices for authentication 2025"
Result: Current 2025 best practices ✅

Research Agent 2:
"Reading: src/auth/ (existing implementation)"
"Recommendation: Extend existing auth, don't rewrite" ✅

Research Agent 3:
"Reading: ARCHITECTURE.md"
"Spec says: Use REST API"
"Recommendation: Follow spec, use REST" ✅

Quality: High (current, reuses existing, follows specs)
```

---

## 🎯 Implementation Plan

### Phase 1: Create Context Hook

1. Create `hooks/context_injector.py`
2. Implement context extraction:
   - Current date
   - Tech stack detection
   - Spec discovery
   - Recent plans
3. Implement context formatting
4. Test hook in isolation

### Phase 2: Update Hook Configuration

5. Update `hooks/hooks.json` to include context injector
6. Test hook chain (context → intent detection)
7. Verify context appears in prompts

### Phase 3: Update Research Agent Templates

8. Add context awareness to all 5 research agent prompts
9. Add grounding rules:
   - Use current date
   - Check specs first
   - Search codebase
   - Follow tech stack
10. Test with real research scenarios

### Phase 4: Update Planning Command

11. Update `slashsense-parallel-plan.md`:
    - Expect context in prompts
    - Reference context in research
    - Validate against specs
12. Test planning with context injection

### Phase 5: Integration Testing

13. Test complete flow:
    - User runs plan command
    - Context injected
    - Research agents receive context
    - Research is grounded
14. Validate improvements:
    - Current date used in searches
    - Specs referenced
    - Existing code not duplicated

---

## ✅ Success Criteria

**Context Injection:**
- [ ] Hook extracts current date from environment
- [ ] Hook detects tech stack from package.json
- [ ] Hook finds existing specifications
- [ ] Hook finds recent plans
- [ ] Context injected into relevant prompts

**Research Grounding:**
- [ ] Web searches use current year (2025, not 2024)
- [ ] Research agents check specs before searching
- [ ] Research agents search codebase for existing patterns
- [ ] Research agents follow tech stack constraints
- [ ] Research agents reference recent plans

**Quality Improvements:**
- [ ] No outdated web search results
- [ ] No duplicate implementations
- [ ] No violations of existing specs
- [ ] No incompatible library recommendations
- [ ] Higher quality, more relevant research

---

## 📝 Example: Context-Grounded Research Flow

### User Request
```
User: /slashsense:parallel:plan
"I need to add user authentication"
```

### Context Injection (Hook)
```
📋 RESEARCH CONTEXT:
Current Date: 2025-10-21
Tech Stack: Python 3.10+, UV
Existing Specs: docs/ARCHITECTURE.md, README.md
Recent Plans: None
```

### Research Agent 1 (With Context)
```
Task: Web search for auth best practices

Context awareness:
✅ Searches: "Python authentication best practices 2025"
✅ NOT: "authentication best practices 2024" (outdated!)

Finds: Latest 2025 Python auth libraries
```

### Research Agent 2 (With Context)
```
Task: Check codebase for existing auth

Context awareness:
✅ First: grep -r "auth" src/
✅ Finds: src/auth/ already exists!
✅ Reads: src/auth/login.py, src/auth/session.py

Recommendation: "Extend existing auth system, don't rewrite"
```

### Research Agent 3 (With Context)
```
Task: Check specifications

Context awareness:
✅ Reads: docs/ARCHITECTURE.md
✅ Finds: "Authentication: Use JWT tokens with 24h expiry"
✅ Spec already defines approach!

Recommendation: "Follow spec: Implement JWT with 24h expiry"
```

### Result: High-Quality, Grounded Research
```
Planning Agent receives:
✅ Current 2025 best practices
✅ Knowledge of existing auth code
✅ Spec compliance (JWT with 24h expiry)

Creates plan:
"Extend existing src/auth/ with JWT tokens (24h expiry) per spec"

NOT:
❌ "Implement new auth from scratch" (duplicates existing!)
❌ "Use OAuth" (violates spec!)
❌ "2024 best practices" (outdated!)
```

---

## 🚀 Impact

**Before:**
- Research was generic and outdated
- Ignored existing codebase
- Violated specifications
- Recommended incompatible technologies

**After:**
- Research is current (2025)
- Builds on existing code
- Follows specifications
- Recommends compatible technologies

**Result:**
- Higher quality plans
- Less duplicate work
- Faster execution (reuse existing)
- Spec compliance
