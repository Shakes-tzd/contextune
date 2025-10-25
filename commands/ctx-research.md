---
name: ctx:research
description: Fast research using 3 parallel Haiku agents for technical questions and decision-making (1-2 min)
keywords:
  - quick research
  - fast research
  - parallel research
  - technical research
  - investigate question
  - research question
executable: true
---

# Contextune Research - Quick Technical Investigation

Conduct focused research using 3 parallel Haiku agents to answer specific technical questions quickly.

## Use Cases

- "What's the best React state library in 2025?"
- "Should I use REST or GraphQL for this API?"
- "What testing frameworks work with Python 3.12?"
- "Does our codebase already handle authentication?"

## How It Works

1. **You ask a research question**
2. **3 parallel agents execute** (1-2 min total):
   - **Agent 1: Web Research** - Latest trends, comparisons, best practices
   - **Agent 2: Codebase Search** - Existing patterns, reuse opportunities
   - **Agent 3: Dependency Analysis** - What's installed, compatibility
3. **Synthesis** - Combined findings with recommendation
4. **Result** - Comparison table + actionable next steps

## Agent Specifications

### Agent 1: Web Research

Searches the web for current information:

```markdown
Research {QUESTION} using WebSearch.

Current date: {CURRENT_DATE}
Tech stack: {TECH_STACK}

Search queries:
- '{QUESTION} best practices {CURRENT_YEAR}'
- '{QUESTION} comparison latest'
- '{QUESTION} recommendations {CURRENT_YEAR}'

Report format (<500 words):
1. **Top 3 Options Found**
2. **Comparison Table** (pros/cons for each)
3. **Current Trends** (what's popular/recommended)
4. **Recommendation** with reasoning

Focus on recent information (2024-2025 preferred).
```

**Expected output:** Comparison of top solutions with pros/cons

---

### Agent 2: Codebase Search

Searches existing code for patterns:

```markdown
Search codebase for existing solutions to {QUESTION}.

Use Grep/Glob to find:
- Similar functionality: grep -r '{KEYWORDS}' .
- Relevant files: glob '**/*{pattern}*'
- Existing implementations

**CRITICAL**: If similar code exists, recommend REUSING it!

Report format (<400 words):
1. **Existing Functionality** (file:line references)
2. **Patterns to Follow** (coding style, architecture)
3. **Recommendation**:
   - REUSE: If good solution exists
   - NEW: If nothing suitable found
   - ENHANCE: If partial solution exists

Include specific file paths and line numbers.
```

**Expected output:** What already exists that can be reused

---

### Agent 3: Dependency Analysis

Analyzes dependencies and compatibility:

```markdown
Analyze dependencies for {QUESTION}.

Check these files:
- package.json (Node/JavaScript)
- pyproject.toml / requirements.txt (Python)
- go.mod (Go)
- Cargo.toml (Rust)
- composer.json (PHP)

Report format (<300 words):
1. **Can Reuse**: Existing dependencies that solve this
2. **Need to Add**: New dependencies required
3. **Compatibility Notes**: Version conflicts, breaking changes
4. **Installation**: Exact commands to install

Example:
Can reuse: pg@8.11.0 (PostgreSQL driver already installed)
Need to add: pg-promise@11.5.4 (better async support)
Compatible: Both work with Node 18+
Install: npm install pg-promise
```

**Expected output:** What's available vs what's needed

---

## Synthesis Format

After all 3 agents complete, synthesize findings:

```markdown
## Research Results: {QUESTION}

### Web Research (Agent 1)
{Top 3 options with pros/cons}

### Codebase Analysis (Agent 2)
{Existing code to reuse OR "No existing solution found"}

### Dependencies (Agent 3)
{What's available, what needs installation}

---

## Recommendation

**Option:** {Recommended approach}

**Reasoning:**
- {Why this option - reference findings from all 3 agents}
- {Supporting evidence from web research}
- {Reuse opportunities from codebase}
- {Dependency considerations}

**Next Steps:**
1. {Actionable item 1}
2. {Actionable item 2}
3. {Actionable item 3}

---

**Cost:** $0.06-0.08 (3 Haiku agents × ~$0.02 each)
**Time:** 1-2 minutes (parallel execution)
```

---

## Example Usage

**User:** "/ctx:research What's the best database for user authentication?"

**Result:**

```markdown
## Research Results: Best Database for User Authentication

### Web Research
Top 3 options for auth storage:
1. **PostgreSQL** - Battle-tested, ACID compliance, excellent for relational user data
2. **Redis** - Fast in-memory, perfect for sessions/tokens, not for primary user storage
3. **MongoDB** - Flexible schema, good for user profiles with varying attributes

### Codebase Analysis
Found existing: PostgreSQL connection in src/db/connection.ts:12
Pattern: Using pg-promise for async queries
Recommendation: **REUSE** PostgreSQL (already configured)

### Dependencies
Can reuse:
- pg@8.11.0 (PostgreSQL driver - installed)
- bcrypt@5.1.0 (password hashing - installed)

Need to add: None
Compatibility: ✅ All compatible with Node 18+

---

## Recommendation

**Option:** PostgreSQL

**Reasoning:**
- Already configured in codebase (connection.ts:12)
- Team familiar with SQL and pg-promise
- Handles relational user data excellently
- ACID compliance ensures data integrity for auth
- No new dependencies needed

**Next Steps:**
1. Create users table migration
2. Add bcrypt password hashing (already available)
3. Implement session management with pg-sessions
4. Consider Redis for session storage later (optimization)

---

**Cost:** $0.07
**Time:** 1.2 minutes
```

---

## Differences from `/ctx:plan`

| Feature | `/ctx:research` | `/ctx:plan` |
|---------|----------------|------------|
| **Purpose** | Answer specific question | Create execution plan |
| **Agents** | 3 (focused) | 5 (comprehensive) |
| **Output** | Findings + recommendation | Structured task plan with dependencies |
| **Time** | 1-2 min | 2-3 min |
| **Cost** | $0.06-0.08 | $0.10-0.12 |
| **Use When** | Quick decision needed | Ready to execute in parallel |
| **Next Step** | User decides | Execute with `/ctx:execute` |

---

## When to Use This Command

**Use `/ctx:research` when:**
- ✅ You need to make a technical decision
- ✅ Comparing libraries, frameworks, or approaches
- ✅ Want to know what already exists in codebase
- ✅ Checking compatibility or dependencies
- ✅ Need quick answer (1-2 min) not full plan

**Use `/ctx:plan` when:**
- ✅ You have multiple features to implement
- ✅ Need structured task breakdown
- ✅ Ready for parallel execution
- ✅ Want dependency analysis and task ordering

---

## Tips for Better Results

1. **Be Specific**: "best state library for React" > "state management"
2. **Include Context**: "for our e-commerce app" helps agents understand requirements
3. **One Question**: Focus on single decision per research session
4. **Current Tech**: Mention your stack ("we use Python 3.12") for relevant results

---

## Technical Details

**Cost Breakdown:**
- Agent 1 (Web): ~$0.03 (200 input + 500 output tokens)
- Agent 2 (Code): ~$0.02 (150 input + 400 output tokens)
- Agent 3 (Deps): ~$0.02 (100 input + 300 output tokens)
- **Total:** ~$0.07 per research session

**Performance:**
- All 3 agents run in parallel
- Wall clock time: 1-2 minutes (not 3× sequential)
- Uses Haiku 4.5 for cost optimization

**Context Preservation:**
- Agents run in subprocesses
- Your main session context preserved
- Results returned as formatted markdown

---

**Ready to research!** Just ask a technical question and I'll spawn the research agents.
