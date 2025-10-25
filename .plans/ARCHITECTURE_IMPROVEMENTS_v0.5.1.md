# Contextune Architecture Improvements v0.5.1
## Discovery Mechanisms + Research Command

**Date:** 2025-10-24
**Based on:** Deep architecture research + user feedback
**Addresses:** Missing discovery mechanism + standalone research needs

---

## Executive Summary

Research uncovered **2 critical gaps** in Contextune architecture:

1. **No standalone research command** - Research embedded in `parallel:plan`, can't be used independently
2. **Missing Claude discovery mechanism** - Zero skills exist, Claude never proactively suggests Contextune

**Impact:** Users install Contextune but never discover its capabilities

**Solution:** Add 2 skills + 1 research command (total: ~6-8 hours development)

---

## Research Findings

### Claude Code Discovery Mechanisms

| Mechanism | Context Overhead | Discovery Method | Best For |
|-----------|------------------|------------------|----------|
| **Hooks** | 0 passive, ~100 active | Manual config | Event-driven automation |
| **Skills** | ~200 tokens passive | Auto-discovered from directories | Proactive suggestions |
| **Commands** | ~30 tokens each (metadata) | Auto-discovered from directories | User-initiated actions |

**Conclusion:** Hooks + Skills hybrid provides optimal discovery with minimal context

### Modern Planning Workflows

**Standard Phases:**
1. **Research/Exploration** - Gather context, assess feasibility (10-20% of time)
2. **Planning** - Transform research into execution plan
3. **Execution** - Implement with adaptive feedback loops
4. **Evaluation** - Measure results, optimize

**Contextune Currently:** Merges research + planning into one command (not modular)

### Context Optimization Patterns

**Optimal Pattern:** Fragment-Based Lazy Loading + Selective Activation

- Load metadata (descriptions) always
- Load full docs only when executed
- **Result:** 10x context reduction (30 vs 300+ tokens baseline)

---

## Current Contextune Architecture

### Existing Components

```
Hooks:
├─ context_injector.js (UserPromptSubmit) - Injects current context
└─ user_prompt_submit.py (UserPromptSubmit) - Intent detection (3-tier)

Commands:
├─ contextune-config.md - Configuration
├─ contextune-stats.md - Statistics
├─ contextune-verify.md - Verification
├─ contextune-parallel-plan.md - Plan creation (RESEARCH EMBEDDED HERE!)
├─ contextune-parallel-execute.md - Execution
├─ contextune-parallel-status.md - Monitoring
└─ contextune-parallel-cleanup.md - Cleanup

Skills: NONE (❌ Critical gap!)

Agents: 5 referenced (parallel-task-executor, worktree-manager, etc.)
```

### Current Workflow

```
User types: "implement auth, dashboard, API"
  ↓
[Hook detects intent] ✓
  ↓
??? NO PROACTIVE SUGGESTION ???  ← Discovery gap!
  ↓
/contextune:parallel:plan
  ├─ Lines 45-248: Research phase (embedded)
  ├─ Spawns 5 Haiku agents for research
  └─ Creates plan with research synthesis
  ↓
/contextune:parallel:execute
```

**Problems:**
1. Research can't be used standalone
2. Claude never suggests "You could parallelize this!"
3. Users don't discover Contextune exists

---

## Proposed Architecture

### New Components

#### 1. Skill: `parallel-development-expert`

**Location:** `.claude/skills/contextune-parallel-development-expert/SKILL.md`

**Purpose:** Proactively suggest parallelization opportunities

**Frontmatter:**
```yaml
---
name: contextune:parallel-development-expert
description: Expert guidance on parallel development workflows using git worktrees and multi-agent execution. Use when users mention parallel work, concurrent development, speeding up development, working on multiple features simultaneously, or scaling team productivity. Activate for questions about task decomposition, worktree management, or parallelization strategies.
---
```

**Content Structure:**
```markdown
# Parallel Development Expert

You are an expert in parallel development workflows using Contextune.

## When to Activate

Activate when user mentions:
- Multiple independent tasks ("implement X, Y, Z")
- Speed concerns ("this will take forever", "too slow")
- Team scaling ("how to parallelize work")
- Worktree questions

## Analysis Criteria

Determine if tasks are independent:
- ✅ Touch different files
- ✅ Different modules/features
- ✅ No shared state
- ❌ Sequential dependencies

## What to Suggest

If 3+ independent tasks detected:

"I can parallelize these tasks using Contextune! Estimated time:
- Sequential: {X} hours
- Parallel: {Y} hours
- Savings: {Z}% faster

Want me to create a parallel development plan?"

Then offer: `/contextune:parallel:plan`

## Examples

User: "I need to add auth, dashboard, and API integration"
You: "These 3 features are independent! I can run them in parallel using git worktrees with Contextune. Estimated: 2.5h parallel vs 6h sequential (58% faster). Shall I create a plan?"

User: "This will take weeks to build all these features"
You: "I can help speed this up! Are the features independent? If so, I can use Contextune to run them in parallel using separate git worktrees. This could reduce development time by 60-80%."
```

**Context Overhead:** ~150 tokens (description + activation hints)

**Activation Frequency:** 5-10% of conversations (only when multiple tasks mentioned)

---

#### 2. Skill: `intent-recognition`

**Location:** `.claude/skills/contextune-intent-recognition/SKILL.md`

**Purpose:** Help users discover Contextune capabilities

**Frontmatter:**
```yaml
---
name: contextune:intent-recognition
description: Help users discover Contextune capabilities and understand how to use natural language commands. Use when users ask about Contextune features, available commands, how to use the plugin, or what they can do. Activate for questions like "what can Contextune do?", "how do I use this?", "show me examples", "what commands are available?"
---
```

**Content Structure:**
```markdown
# Contextune Intent Recognition & Discovery

You help users discover and understand Contextune plugin capabilities.

## When to Activate

- "What can Contextune do?"
- "How do I use this plugin?"
- "Show me Contextune examples"
- "What commands are available?"
- "Contextune documentation"

## Capabilities Overview

Contextune provides **natural language to slash command mapping** with three tiers:

1. **Intent Detection** (automatic)
   - Detects slash commands from natural language
   - 3-tier cascade: Keyword → Model2Vec → Semantic Router
   - Confidence scoring

2. **Parallel Development** (workflow)
   - Research → Plan → Execute → Cleanup
   - Git worktree-based parallel execution
   - Multi-agent coordination

3. **Configuration** (optional)
   - `/contextune:config` - View/edit settings
   - `/contextune:stats` - Usage statistics

## Natural Language Examples

Instead of typing `/sc:analyze`, users can say:
- "analyze my code"
- "review this codebase"
- "check code quality"

Contextune automatically detects and suggests the command.

## Available Commands

### Research & Planning
- `/contextune:research` - Standalone research (quick questions)
- `/contextune:parallel:plan` - Create parallel development plan

### Execution & Monitoring
- `/contextune:parallel:execute` - Execute plan with worktrees
- `/contextune:parallel:status` - Monitor progress
- `/contextune:parallel:cleanup` - Clean up worktrees

### Configuration
- `/contextune:config` - Manage settings
- `/contextune:stats` - View statistics
- `/contextune:verify` - Verify detection

## How to Use

**Option 1: Natural Language (Recommended)**
Just type what you want: "analyze my code"
Contextune detects and suggests the appropriate command.

**Option 2: Explicit Command**
Type `/command-name` directly.

## Example Conversation

User: "What can this plugin do?"
You: [Show capabilities overview + natural language examples]

User: "How do I parallelize work?"
You: "Use natural language like 'create parallel plan for features X, Y, Z' or run `/contextune:parallel:plan` directly."
```

**Context Overhead:** ~50 tokens (description only)

**Activation Frequency:** 1-2% of conversations (only when explicitly asked)

---

#### 3. Command: `/contextune:research`

**Location:** `commands/contextune-research.md`

**Purpose:** Standalone research without parallel execution commitment

**Frontmatter:**
```yaml
---
name: contextune:research
description: Conduct focused research using parallel Haiku agents. Answers questions about libraries, best practices, existing code patterns, and technical decisions. Returns findings without creating a full development plan.
executable: true
---
```

**Content Structure:**
```markdown
# Contextune Research - Focused Investigation

Conduct targeted research using 3 parallel Haiku agents to answer specific questions.

## Use Cases

- "What's the best React state library in 2025?"
- "Should I use REST or GraphQL for this API?"
- "Does our codebase already handle authentication?"
- "What testing frameworks are popular for Python?"

## Workflow

1. User asks research question
2. Spawn 3 parallel agents (1-2 min total):
   - Agent 1: Web search (latest trends, comparisons)
   - Agent 2: Codebase search (existing patterns, reuse opportunities)
   - Agent 3: Dependency analysis (what's installed, compatibility)
3. Synthesize findings
4. Return comparison table + recommendation

## Agent Specifications

### Agent 1: Web Research

```
Task tool with subagent_type="general-purpose"

Prompt:
"Research {QUESTION} using WebSearch.

Current date: {CURRENT_DATE}
Tech stack: {TECH_STACK}

Search queries:
- '{QUESTION} best practices {CURRENT_YEAR}'
- '{QUESTION} comparison latest'

Report (<500 words):
1. Options found (top 3)
2. Comparison table (pros/cons)
3. Recommendation with reasoning
4. Current trends"
```

### Agent 2: Codebase Search

```
Task tool with subagent_type="general-purpose"

Prompt:
"Search codebase for existing solutions to {QUESTION}.

Use Grep/Glob:
- grep -r '{KEYWORDS}' . --include='*.{ext}'
- Check for similar functionality

CRITICAL: If similar code exists, recommend REUSING it!

Report (<400 words):
1. Existing functionality (file:line)
2. Patterns to follow
3. Recommendation (REUSE vs NEW)"
```

### Agent 3: Dependency Analysis

```
Task tool with subagent_type="general-purpose"

Prompt:
"Analyze dependencies for {QUESTION}.

Read:
- package.json (Node)
- pyproject.toml (Python)
- go.mod (Go)
- Cargo.toml (Rust)

Check:
- Relevant existing dependencies
- New dependencies needed
- Compatibility

Report (<300 words):
1. Can reuse: {existing deps}
2. Need to add: {new deps}
3. Compatibility notes"
```

## Synthesis Format

```markdown
## Research Results: {QUESTION}

### Web Research
{Agent 1 findings - top 3 options with pros/cons}

### Codebase Analysis
{Agent 2 findings - existing code to reuse}

### Dependencies
{Agent 3 findings - what's available, what's needed}

### Recommendation

**Option:** {Recommended approach}

**Reasoning:**
- {Why this option}
- {Supporting evidence}

**Next Steps:**
- {Actionable item 1}
- {Actionable item 2}

**Cost:** $0.06-0.08 (3 Haiku agents)
**Time:** 1-2 minutes
```

## Differences from `/parallel:plan`

| Feature | `/research` | `/parallel:plan` |
|---------|-------------|------------------|
| Purpose | Answer specific question | Create execution plan |
| Agents | 3 (focused) | 5 (comprehensive) |
| Output | Findings + recommendation | Structured task plan |
| Time | 1-2 min | 2-3 min |
| Cost | $0.06-0.08 | $0.10-0.12 |
| Next step | User decides | Execute plan |

## Example Usage

**User:** "What's the best database for our use case?"

**Claude:** I'll research database options for you using Contextune.

*Spawns 3 agents in parallel...*

**Result:**
```
## Research Results: Best Database Selection

### Web Research
Top 3 options for {use case}:
1. PostgreSQL - Battle-tested, full SQL, excellent for relational data
2. MongoDB - Flexible schema, great for document storage
3. Redis - Fast in-memory, perfect for caching/sessions

### Codebase Analysis
Found existing: PostgreSQL connection in src/db/connection.ts:12
Recommendation: REUSE PostgreSQL (already configured)

### Dependencies
Can reuse: pg@8.11.0 (already installed)
Need to add: None
Compatibility: ✅ All systems go

### Recommendation

**Option:** PostgreSQL

**Reasoning:**
- Already configured in codebase
- Team familiar with SQL
- Handles relational data well
- No new dependencies needed

**Next Steps:**
- Extend existing connection pool
- Add migration for new tables
- Consider pg-promise for better async support
```

---

## Implementation Steps

**Step 1:** Create skill directory structure
```bash
mkdir -p .claude/skills/contextune-parallel-development-expert
mkdir -p .claude/skills/contextune-intent-recognition
```

**Step 2:** Write SKILL.md files (content above)

**Step 3:** Create `/contextune:research` command

**Step 4:** Test discovery
- Start fresh Claude Code session
- Say "I need to build 3 features"
- Verify skill activates and suggests parallelization

**Step 5:** Test research
- Run `/contextune:research` with question
- Verify 3 agents spawn in parallel
- Check synthesis quality

---

## Updated Workflow

### Discovery Flow (NEW!)

```
User: "I need to implement auth, dashboard, and API"
  ↓
[parallel-development-expert skill activates automatically]
  ↓
Claude: "I can parallelize these! Estimated:
  - Sequential: 6h
  - Parallel: 2.5h (58% faster)

  Want me to create a plan?"
  ↓
[User: "Yes"]
  ↓
/contextune:parallel:plan
```

### Research Flow (NEW!)

```
User: "What's the best state library for React?"
  ↓
/contextune:research
  ├─ Agent 1: WebSearch (Zustand, Redux, Jotai comparison)
  ├─ Agent 2: Codebase (existing patterns)
  └─ Agent 3: Dependencies (what's installed)
  ↓
Synthesis: "Recommend Zustand (lightweight, already using similar pattern)"
  ↓
User decides next action
```

### Planning Flow (ENHANCED!)

```
User: "Create parallel plan for X, Y, Z"
  ↓
[context_injector.js] Injects date, tech stack, specs
  ↓
/contextune:parallel:plan
  ├─ NOW: Can reuse /contextune:research findings!
  ├─ Spawns 5 agents OR references prior research
  └─ Creates structured plan
  ↓
/contextune:parallel:execute
```

---

## Context Overhead Analysis

### Before (Current)

```
Passive (always loaded):
- Commands metadata: ~210 tokens (7 commands × ~30 tokens)
- Skills: 0 tokens (NONE EXIST)
Total passive: ~210 tokens

Active (when triggered):
- Hook execution: ~100 tokens (intent detection result)
- Full command: ~300 tokens (when executed)
Total active: ~400 tokens

Discovery capability: ❌ NONE (no proactive suggestions)
```

### After (Proposed)

```
Passive (always loaded):
- Commands metadata: ~240 tokens (8 commands × ~30 tokens)
- Skills metadata: ~200 tokens (2 skills × descriptions)
Total passive: ~440 tokens

Active (when triggered):
- Hook execution: ~100 tokens (same)
- Skill activation: ~50 tokens (suggestion text)
- Full command: ~300 tokens (when executed)
Total active: ~450 tokens

Discovery capability: ✅ PROACTIVE (skills suggest automatically)
```

**Trade-off:**
- Cost: +230 tokens passive (~$0.0007 per session)
- Benefit: Users discover Contextune automatically
- ROI: Massive (discovery drives adoption)

---

## Implementation Priority

### Phase 1: Discovery (HIGH PRIORITY)

**Why:** Solves the "users don't know Contextune exists" problem

**Tasks:**
1. Create `contextune:parallel-development-expert` skill (2-3h)
2. Create `contextune:intent-recognition` skill (1h)
3. Test discovery in real conversations (30min)

**Deliverables:**
- `.claude/skills/contextune-parallel-development-expert/SKILL.md`
- `.claude/skills/contextune-intent-recognition/SKILL.md`
- Verified: Skills activate automatically

**Estimated Effort:** 3-4 hours

---

### Phase 2: Research Command (MEDIUM PRIORITY)

**Why:** Decouples research from planning (modularity)

**Tasks:**
1. Create `/contextune:research` command (2-3h)
2. Extract research agent templates from `parallel:plan` (1h)
3. Test standalone research (30min)

**Deliverables:**
- `commands/contextune-research.md`
- Verified: Research works independently

**Estimated Effort:** 3-4 hours

---

### Phase 3: Refactor Planning Command (LOW PRIORITY)

**Why:** Remove research duplication, make planning leaner

**Tasks:**
1. Modify `parallel:plan` to optionally reference `/research` results (1-2h)
2. Add "Skip research if already done" logic (1h)
3. Test integrated workflow (30min)

**Deliverables:**
- Updated `commands/contextune-parallel-plan.md`
- Verified: Can reuse research or run fresh

**Estimated Effort:** 2-3 hours

---

## Total Effort

| Phase | Priority | Effort | Impact |
|-------|----------|--------|--------|
| Discovery Skills | HIGH | 3-4h | Massive (solves adoption problem) |
| Research Command | MEDIUM | 3-4h | High (modularity, reusability) |
| Planning Refactor | LOW | 2-3h | Medium (cleanup, efficiency) |
| **Total** | | **8-11h** | |

---

## Success Metrics

### Discovery

**Target:** 80% of users with multiple-task requests see proactive suggestion

**Measurement:**
```python
# Track in contextune-stats
{
  "skill_activations": {
    "parallel-development-expert": {
      "triggered": 45,
      "user_accepted": 38,
      "acceptance_rate": "84%"
    }
  }
}
```

### Research Adoption

**Target:** 50% of planning sessions preceded by `/research`

**Measurement:**
```python
{
  "command_usage": {
    "contextune:research": 23,
    "contextune:parallel:plan": 46,
    "research_before_plan_rate": "50%"
  }
}
```

### Context Efficiency

**Target:** <500 tokens passive overhead

**Measurement:**
- Skill descriptions: ~200 tokens
- Command metadata: ~240 tokens
- **Total: 440 tokens** ✅ Under target

---

## Integration with v0.5.0 Plan

This architecture improvement **complements** the v0.5.0 cost optimization plan:

### Combined Implementation Order

**Week 1:**
- v0.5.0 Phase 1: Cost tracking, contextual help, validator (8-10h)
- v0.5.1 Phase 1: Discovery skills (3-4h)
- **Total: 11-14h wall clock**

**Week 2:**
- v0.5.0 Phase 2: Agent cost advisor, orchestration (12-15h)
- v0.5.1 Phase 2: Research command (3-4h)
- **Total: 15-19h wall clock**

**Week 3:**
- v0.5.0 Phase 3: Testing, documentation (6-8h)
- v0.5.1 Phase 3: Planning refactor (2-3h)
- **Total: 8-11h wall clock**

**Grand Total:** 34-44 hours (vs 42-54h for v0.5.0 alone)

**Synergy:** Discovery skills make cost optimization features more discoverable!

---

## Risk Analysis

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Skills don't activate when expected | High | Low | Test with diverse prompts, iterate on description |
| Skill descriptions exceed context budget | Medium | Very Low | Keep descriptions under 200 chars each |
| Users annoyed by proactive suggestions | Medium | Low | Make suggestions helpful, not pushy; easy to decline |
| Research command too slow | Low | Medium | Use 3 agents (not 5), optimize for speed |

---

## Rollout Strategy

### Phase 1: Stealth Launch (Internal)
- Install skills locally
- Test for 1 week
- Validate activation rate
- Iterate on descriptions

### Phase 2: Beta (v0.5.1-beta)
- Bundle with v0.5.0 release
- Announce discovery improvements
- Collect activation metrics
- Adjust based on feedback

### Phase 3: GA (v0.5.1)
- Release as stable
- Publish discovery metrics
- Create tutorial: "How Contextune discovers itself"

---

## Documentation Updates

### README.md

Add section:

```markdown
## 🔍 Auto-Discovery

Contextune automatically discovers opportunities to help:

### Proactive Suggestions
When you mention multiple tasks, Contextune suggests parallelization:
- "I need to build auth, dashboard, and API"
- → Claude: "I can parallelize these! 58% faster with Contextune"

### Quick Research
Need to make a technical decision? Use `/contextune:research`:
- "What's the best React state library?"
- → Gets comparison in 1-2 minutes using parallel research agents

### Intent Detection
Just use natural language—Contextune detects commands automatically:
- "analyze my code" → Suggests `/sc:analyze`
- "create parallel plan" → Triggers `/contextune:parallel:plan`
```

### New Documentation Files

1. `docs/discovery.md` - How auto-discovery works
2. `docs/research-workflow.md` - Using `/contextune:research`
3. `docs/skills-reference.md` - Available skills and activation criteria

---

## Conclusion

These architecture improvements address the two critical gaps:

1. ✅ **Discovery** - Skills enable proactive suggestions (massive adoption impact)
2. ✅ **Modularity** - Research command decouples research from planning (reusability)

**Investment:** 8-11 hours
**Impact:** Solves the "users don't know Contextune exists" problem
**Context Cost:** +230 tokens (~$0.0007 per session)
**ROI:** Massive (adoption drives all other features)

**Recommendation:** Implement in parallel with v0.5.0 for maximum impact.

---

## Next Steps

1. **Review this plan** - Validate approach
2. **Choose priority** - All phases or just discovery?
3. **Begin Phase 1** - Create skills (highest impact)
4. **Integrate with v0.5.0** - Combined rollout

**Ready to implement?** The architecture is fully specified.