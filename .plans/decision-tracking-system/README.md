# Decision Tracking System - Implementation Plan

**Status:** Design Complete - Ready for /ctx:plan → /ctx:execute
**Created:** 2025-10-27
**Estimated Effort:** 60K tokens (Haiku), $0.070
**Execution Mode:** Parallel (2 phases)

---

## Quick Start

```bash
# Execute the plan
/ctx:plan @.plans/decision-tracking-system/plan.yaml

# Then execute in parallel
/ctx:execute
```

---

## What This Builds

**YAML-based decision tracking** for Contextune to preserve context across sessions:

1. **decisions.yaml** - Main database (like features.yaml)
   - Track research sessions (avoid redundant $0.07 research)
   - Track plans created (reference, don't recreate)
   - Track decisions made (WHY, not just WHAT)

2. **CLI Tools** - Query and manage (like feature-*.py scripts)
   - `decision-search.py` - Filter by type/status/tags
   - `decision-add.py` - Interactive entry creation
   - `decision-report.py` - Auto-generate DECISION_INDEX.md
   - `decision-lifecycle.py` - Archive expired/completed entries

3. **Skill** - Auto-track during conversations
   - Detects: "we researched", "we decided", "why did we choose"
   - Checks: decisions.yaml for existing context
   - Documents: Appends new entries automatically

4. **Hook** - Session end reminder
   - Prompts: "Review decisions made this session"
   - Links: to decision-add.py for easy documentation

---

## Design Principles

### 1. Reuse Existing Patterns (95% Copy)

**Instead of inventing:**
- decisions.yaml = features.yaml structure
- decision-search.py = feature-status.py with search filters
- decision-add.py = feature-execute.py with YAML append
- Skill = researcher skill with decision detection
- Hook = tool_cost_tracker hook with decision reminder

### 2. Template Everything (Haiku-Friendly)

**Every task includes:**
- Complete code template (copy, don't invent)
- Exact file paths and commands
- Validation checklist
- Expected output

### 3. Independent Tasks (Parallel Execution)

```
Phase 1 (all parallel):
  ├─ Task 1: decisions.yaml schema
  ├─ Task 2: decision-search.py
  ├─ Task 3: decision-add.py
  └─ Task 4: decision-lifecycle.py

Phase 2 (all parallel after Phase 1):
  ├─ Task 5: Decision tracker skill
  ├─ Task 6: Session end hook
  └─ Task 7: CLAUDE.md integration
```

---

## Architecture

### Data Structure (decisions.yaml)

```yaml
metadata:         # Project info, retention policy
index:            # Quick counts (research: 3, plans: 2, decisions: 5)

research:         # Research sessions
  - id, topic, findings, references, tags
  - Lifecycle: Expires after 6 months

plans:            # Plans created
  - id, title, summary, references, tags
  - Lifecycle: Archives 90 days after completion

decisions:        # Decisions made
  - id, context, alternatives, decision, consequences
  - Lifecycle: Never auto-archives (unless superseded)

summary:          # Auto-generated statistics
```

### Lifecycle Management

**Research:**
- Active → Expired (6 months) → Archived (quarterly)
- Rationale: Technology/best practices evolve quickly

**Plans:**
- Designed → Completed → Archived (90 days)
- Rationale: Reference during implementation, archive after

**Decisions:**
- Accepted → Never auto-archives
- Only archived if explicitly superseded

**Archive Strategy:**
```
docs/archive/
  ├── decisions-2025-Q1.yaml
  ├── decisions-2025-Q2.yaml
  └── decisions-2025-Q3.yaml
```

### Token Efficiency

| Time | Active File | Archives | Claude Loads |
|------|-------------|----------|--------------|
| Month 1 | 5K tokens | 0 | 5K |
| Month 6 | 8K tokens | 2K | 8K |
| Year 1 | 10K tokens | 15K | 10K |
| Year 5 | 10K tokens | 80K | 10K |

**Key insight:** Active file stays <10K tokens due to lifecycle management.

---

## Future: RAG Integration (Phase 2)

**Trigger:** When active file exceeds 100 entries despite lifecycle

**Architecture:**
```
decisions.yaml (active, <10K tokens)
    ↓ (monthly embedding)
vector_db/
  ├── research.index
  ├── plans.index
  └── decisions.index

Query: "How do we handle tokens?"
  → Semantic search finds top 3 relevant entries
  → Load only those (~2K tokens vs 60K)
```

**Benefits:**
- Semantic search ("cost optimization" finds "token estimation")
- Token ceiling: ~5K max (no matter how many entries)
- Works with archives (search all time)

**Tools:**
- Vector DB: Chroma/LanceDB (free, local)
- Embeddings: Model2Vec (already in Contextune!)
- Cost: $0 (all local, no APIs)

---

## Task Breakdown

### Phase 1: Foundation (30-45 min, parallel)

**Task 1: Create decisions.yaml** (12K tokens)
- Copy template from plan
- Validate YAML syntax
- Test Python can read it

**Task 2: Create decision-search.py** (12K tokens)
- Copy feature-status.py structure
- Adapt to read decisions.yaml
- Add filters: type, status, tags

**Task 3: Create decision-add.py** (12K tokens)
- Copy feature-execute.py structure
- Add interactive prompts
- Append to decisions.yaml

**Task 4: Create decision-lifecycle.py** (12K tokens)
- Archive expired research (>6 months)
- Archive completed plans (>90 days)
- Generate quarterly archives

### Phase 2: Integration (20-30 min, parallel)

**Task 5: Create Decision Tracker Skill** (15K tokens)
- Copy researcher skill structure
- Add decision detection keywords
- Check decisions.yaml before research
- Append entries after decisions

**Task 6: Create Session End Hook** (8K tokens)
- Copy tool_cost_tracker hook
- Check decisions made in session
- Remind to review/document

**Task 7: Update CLAUDE.md** (13K tokens)
- Run decision-report.py to generate DECISION_INDEX.md
- Import DECISION_INDEX.md in CLAUDE.md
- Update documentation guidelines

### Phase 3: Validation (10-15 min)

**Task 8: Testing** (8K tokens)
- Validate all files exist
- Run all CLI tools
- Test skill detection
- Test hook invocation
- Verify CLAUDE.md import

---

## Success Criteria

✅ **Functional:**
- decisions.yaml exists and is valid
- CLI tools work (search, add, lifecycle)
- Skill auto-invokes on decision discussions
- Hook reminds at session end
- CLAUDE.md imports index

✅ **Performance:**
- Token overhead <10K for active file
- Search completes in <100ms
- Lifecycle runs in <1s

✅ **Usability:**
- Zero manual work (skill handles it)
- Clear validation at each step
- Documentation complete

---

## Rollback Plan

- Keep decisions.yaml (even if tools incomplete)
- Can be queried manually with yq/python
- Remove skill/hook if causing issues
- Disable CLAUDE.md import if too verbose

---

## Files in This Plan

```
.plans/decision-tracking-system/
├── README.md (this file)
├── plan.yaml (complete plan for /ctx:plan)
├── tasks/
│   ├── task-1.md (decisions.yaml schema) ✅ COMPLETE
│   ├── task-2.md (decision-search.py) - TO CREATE
│   ├── task-3.md (decision-add.py) - TO CREATE
│   ├── task-4.md (decision-lifecycle.py) - TO CREATE
│   ├── task-5.md (skill) - TO CREATE
│   ├── task-6.md (hook) - TO CREATE
│   ├── task-7.md (CLAUDE.md) - TO CREATE
│   └── task-8.md (validation) - TO CREATE
└── templates/
    ├── decisions.yaml.template - IN TASK-1
    ├── decision-search.template.py - TO CREATE
    ├── decision-add.template.py - TO CREATE
    └── SKILL.template.md - TO CREATE
```

---

## Next Steps

1. **Complete remaining task files** (tasks 2-8)
2. **Add this to CHANGELOG** with complete context
3. **Commit plan** to repository
4. **Execute when ready:** `/ctx:plan` → `/ctx:execute`

---

**Ready for Haiku blind execution!**
