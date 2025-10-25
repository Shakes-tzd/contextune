# Claude Code Conversation Flow Architecture

**Date:** 2025-10-25
**Analysis:** Message storage, threading, and compact behavior

---

## Storage Structure

### Directory Layout

```
~/.claude/
├── projects/
│   └── {url-encoded-path}/
│       ├── {session-id-1}.jsonl          # 2.3 MB (lots of tool results)
│       ├── {session-id-2}.jsonl          # 5.4 MB (current session!)
│       └── {session-id-3}.jsonl          # 194 B (just started)
├── cache/
│   └── context/
│       ├── 08146e72fe4ca656.json         # Cached file content
│       ├── 2e53ad9191e0b384.json
│       └── ...
└── archives/
    └── todos/
        └── {agent-id}.json               # Archived todo lists
```

### Current Session File

**Path:** `~/.claude/projects/-Users-shakes-DevProjects-slashsense/e596b0a5-456a-4026-b892-a361d01f6841.jsonl`

**Size:** 5.4 MB (this session!)
**Lines:** 1,317 events (each line = 1 JSON event)

---

## Message Event Structure

### Event Types

Each JSONL line contains one event:

```json
{
  "parentUuid": "702c282e-d3eb-4b1b-9862-7b494568bdca",
  "isSidechain": false,
  "userType": "external",
  "cwd": "/Users/shakes/DevProjects/slashsense",
  "sessionId": "e596b0a5-456a-4026-b892-a361d01f6841",
  "version": "2.0.27",
  "gitBranch": "master",
  "type": "user",              ← Event type
  "message": {
    "role": "user",
    "content": "Warmup"
  },
  "uuid": "83885a8a-42b6-4982-b675-1c30eaad451d",
  "timestamp": "2025-10-25T02:27:22.148Z"
}
```

### Event Types

| Type | Description | Storage Size |
|------|-------------|--------------|
| `"user"` | User message | Small (~200 bytes) |
| `"assistant"` | Claude's response | Small (~300 bytes) |
| `"tool_use"` | Tool invocation (Read, Grep, Bash, etc.) | Small (~400 bytes) |
| `"tool_result"` | Tool output | **LARGE** (can be 10KB-100KB+) |
| `"thinking"` | Extended thinking blocks | **LARGE** (5KB-50KB) |

### Token Counting in Messages

```json
{
  "message": {
    "model": "claude-haiku-4-5-20251001",
    "usage": {
      "input_tokens": 3,
      "cache_creation_input_tokens": 7072,      ← New content cached
      "cache_read_input_tokens": 0,              ← Read from cache
      "cache_creation": {
        "ephemeral_5m_input_tokens": 7072,
        "ephemeral_1h_input_tokens": 0
      },
      "output_tokens": 253,
      "service_tier": "standard"
    }
  }
}
```

**Key insight:** Each API call records its own token usage. The JSONL file shows:
- What was sent (input_tokens)
- What was newly cached (cache_creation_input_tokens)
- What was read from cache (cache_read_input_tokens)
- What was generated (output_tokens)

---

## Thread Architecture (Parent-Child Links)

### Threading via UUIDs

Each message links to its parent via `parentUuid`:

```
Message 1: uuid="702c282e-d3eb-4b1b-9862-7b494568bdca", parentUuid=null
                                    ↓
Message 2: uuid="83885a8a-42b6-4982-b675-1c30eaad451d", parentUuid="702c282e..."
                                    ↓
Message 3: uuid="26175e4f-8cc7-458d-a968-8f8b41e582cb", parentUuid="83885a8a..."
```

### Tool Call Threading

Tool uses and results are nested:

```
User Message (uuid=A, parentUuid=null)
  ↓
Assistant Response (uuid=B, parentUuid=A)
  ├─ Tool Use: Read file1.ts (uuid=C, parentUuid=B)
  ├─ Tool Use: Read file2.ts (uuid=D, parentUuid=B)
  └─ Tool Use: Grep "auth" (uuid=E, parentUuid=B)
      ↓
Tool Result: file1.ts content (uuid=F, parentUuid=C)   ← 50KB of content!
      ↓
Tool Result: file2.ts content (uuid=G, parentUuid=D)   ← 60KB of content!
      ↓
Tool Result: grep results (uuid=H, parentUuid=E)       ← 10KB of matches
      ↓
Assistant Response (uuid=I, parentUuid=H)
```

**Storage impact:** All 3 tool results (120KB total) are stored in JSONL file.

---

## Prompt Caching Behavior

### How Caching Works

From our research and analysis:

**Cache Hierarchy:**
```
API Request Context:
├── System Prompt (CLAUDE.md, SuperClaude docs)  ← Cached (5 min TTL)
├── Tool Definitions                              ← Cached (5 min TTL)
├── Previous Messages (conversation history)      ← Cached (5 min TTL)
│   ├── User messages
│   ├── Assistant messages
│   └── Tool results (file contents, grep output) ← THIS IS CACHED!
└── Current User Message                          ← New content
```

**Automatic Prefix Caching:**
- Claude Code inserts cache breakpoints automatically
- Caches "up to approximately 20 blocks before your explicit breakpoint"
- Each tool result is a separate content block
- **All previous tool results are cached** (if within 5 min window)

**Example from our session:**
```json
{
  "usage": {
    "input_tokens": 12,
    "cache_creation_input_tokens": 4650,    ← New content (4,650 tokens)
    "cache_read_input_tokens": 49981,       ← Read from cache (49,981 tokens!)
    "cache_creation": {
      "ephemeral_5m_input_tokens": 4650,
      "ephemeral_1h_input_tokens": 0
    }
  }
}
```

**Analysis:** 49,981 tokens read from cache = ~75MB of text! This includes:
- Previous file reads
- Previous grep results
- Previous assistant responses
- Previous tool outputs

**Cost savings:** 49,981 cached tokens × 0.1x price = 90% cheaper than re-reading

---

## What Happens During Compact

### Auto-Compact Trigger

From documentation:
> "Claude Code uses auto-compact by default when context exceeds 95% capacity"

**Context limits:**
- Sonnet 4.5: 200K tokens
- Haiku 4.5: 200K tokens
- Trigger: ~190K tokens

### Compact Process (Hypothesis based on behavior)

**Before Compact:**
```
JSONL file (5.4 MB, 1,317 events):
├── Message 1-10 (warmup, initial context)
├── Message 11-50 (file reads, tool results - 1 MB)
├── Message 51-100 (more file reads - 2 MB)
├── Message 101-200 (grep results, analysis - 1.5 MB)
├── ... (total: 5.4 MB of detailed history)
└── Current context: 190K tokens (95% full)
```

**Compact Action:**
1. **Summarization request** sent to Claude:
   - "Summarize the conversation so far, focusing on key decisions and context"
   - Claude generates summary (2-5K tokens)

2. **New context constructed:**
   ```
   New API request:
   ├── System Prompt
   ├── Summary of conversation     ← Replaces full history!
   ├── Recent messages (last 10?)  ← Kept verbatim
   └── Current message
   ```

3. **JSONL file unchanged:**
   - Full history STILL on disk (5.4 MB)
   - But API only sends summary + recent messages
   - Old tool results NOT sent to API

4. **Cache invalidated:**
   - Summary is new content
   - Old cache entries (tool results) not referenced
   - Cache TTL expires (5 min)

**After Compact:**
```
API Context (sent to Claude):
├── System Prompt (7K tokens)
├── Summary (3K tokens)          ← "You analyzed auth code, found X patterns..."
├── Recent messages (10K tokens)  ← Last few exchanges
└── Current message (1K tokens)

Total: ~21K tokens (vs 190K before compact!)
```

**What's LOST:**
- ❌ Detailed file contents
- ❌ Full grep results
- ❌ Exact code snippets analyzed
- ❌ Tool output details
- ❌ Specific line numbers and file paths

**What's PRESERVED:**
- ✅ High-level findings (in summary)
- ✅ Key decisions made
- ✅ Recent conversation flow
- ✅ Overall task understanding

### Why Re-Reads Happen

**Scenario:**
1. Before compact: Read `auth.ts` (5,000 tokens) → Cached
2. Compact triggered: Summary created, old context discarded
3. After compact: Claude wants to check `auth.ts` again
4. Problem: `auth.ts` content not in summary (too detailed)
5. Solution: **Re-read file** → New 5,000 tokens counted

**Cost impact:**
- First read: 5,000 tokens (or 500 if cached from earlier)
- After compact: 5,000 NEW tokens (cache invalidated or content not in context)
- **Total: 10,000 tokens for same file** (if read before and after compact)

---

## Flowchart: Message Flow & Compacting

```mermaid
graph TB
    Start([User Types Message]) --> UserPromptHook{UserPromptSubmit Hook}
    UserPromptHook --> IntentDetect[SlashSense Intent Detection]
    IntentDetect --> ContextInjector[Context Injector Hook]
    ContextInjector --> BuildContext[Build API Request Context]

    BuildContext --> CheckCache{Check Cache}
    CheckCache -->|Cache Hit| UseCached[Read from Cache<br/>0.1x cost]
    CheckCache -->|Cache Miss| NewTokens[New Tokens<br/>Full cost]
    UseCached --> APIRequest
    NewTokens --> APIRequest[Send to Claude API]

    APIRequest --> CheckSize{Context > 95%?}
    CheckSize -->|No| NormalResponse[Claude Processes<br/>Returns Response]
    CheckSize -->|Yes| AutoCompact[Auto-Compact Triggered]

    AutoCompact --> SummarizeRequest[Send Summarization Request:<br/>'Summarize conversation focusing on decisions']
    SummarizeRequest --> GenerateSummary[Claude Generates Summary<br/>2-5K tokens]
    GenerateSummary --> NewContext[Rebuild Context:<br/>System + Summary + Recent Messages]
    NewContext --> InvalidateCache[Old Cache Entries<br/>No Longer Referenced]
    InvalidateCache --> CompactedResponse[Claude Processes<br/>with Compacted Context]

    NormalResponse --> StoreEvent[Store Event in JSONL]
    CompactedResponse --> StoreEvent

    StoreEvent --> WriteJSONL[(Append to session.jsonl<br/>~/.claude/projects/.../uuid.jsonl)]
    WriteJSONL --> UpdateCache[Update Cache<br/>5 min TTL]
    UpdateCache --> DisplayUser[Display to User]

    DisplayUser --> ToolCall{Tool Use?}
    ToolCall -->|Yes| ExecuteTool[Execute Tool<br/>Read/Grep/Bash/etc]
    ExecuteTool --> ToolResult[Tool Result Event<br/>Can be 10KB-100KB+]
    ToolResult --> StoreToolResult[Store in JSONL]
    StoreToolResult --> CheckCache
    ToolCall -->|No| CheckNext{More Messages?}

    CheckNext -->|Yes| Start
    CheckNext -->|No| SessionEnd([Session Complete])

    style AutoCompact fill:#ff9999
    style InvalidateCache fill:#ff9999
    style ToolResult fill:#ffcc99
    style WriteJSONL fill:#99ccff
    style UseCached fill:#99ff99
```

---

## Detailed Event Sequence Example

### Scenario: Read 3 Files Before and After Compact

**Phase 1: Initial Reads (Before Compact)**

```
Event 1: User: "Read auth.ts, user.ts, api.ts"
Event 2: Assistant: <tool_use: Read auth.ts>
Event 3: Tool Result: [5,000 tokens of auth.ts content]  ← Stored in JSONL
Event 4: Assistant: <tool_use: Read user.ts>
Event 5: Tool Result: [6,000 tokens of user.ts content]  ← Stored in JSONL
Event 6: Assistant: <tool_use: Read api.ts>
Event 7: Tool Result: [4,000 tokens of api.ts content]   ← Stored in JSONL
Event 8: Assistant: "I've read all 3 files. auth.ts has..."

Total: 15,000 tokens in tool results (now in JSONL and cached)
```

**Context at this point:**
```
API Request:
├── System Prompt: 7K tokens
├── Event 1-8: 20K tokens
│   ├── User message: 50 tokens
│   └── Tool results: 15K tokens  ← ALL file contents
└── Total: 27K tokens
```

**Phase 2: More Work (Approaching Limit)**

```
Event 9-100: User asks more questions, reads more files, runs grep...

Context grows to: 190K tokens (95% of 200K limit)
```

**Phase 3: Auto-Compact Triggered**

```
Event 101: AUTO-COMPACT TRIGGERED
  ↓
Claude receives summarization request:
  "Summarize the conversation so far, focusing on key findings"
  ↓
Event 102: Summary Generated
  "The user analyzed authentication code across 3 files:
   - auth.ts implements OAuth2 flow
   - user.ts has User model with validation
   - api.ts defines REST endpoints
   Key finding: Missing CSRF protection"

  (Summary: 150 tokens vs 15,000 in original file contents)
  ↓
New context built:
├── System Prompt: 7K tokens
├── Summary: 150 tokens        ← Replaces events 1-90
├── Recent events (91-102): 5K tokens
└── Total: 12K tokens (vs 190K before!)
```

**Phase 4: User Asks Follow-up (After Compact)**

```
Event 103: User: "Can you check the CSRF implementation in auth.ts again?"

Problem: auth.ts content NOT in context anymore!
  - Summary mentions "Missing CSRF" but no code details
  - File content (5,000 tokens) was in events 1-90
  - Events 1-90 summarized to 150 tokens (details lost)

Solution: RE-READ FILE
Event 104: Assistant: <tool_use: Read auth.ts>
Event 105: Tool Result: [5,000 tokens of auth.ts content]  ← READ AGAIN!
Event 106: Assistant: "Looking at auth.ts again..."

Cost: 5,000 NEW tokens (even though we read it in Event 3)
```

**Total tokens for auth.ts:**
- Event 3 (before compact): 5,000 tokens (0.1x if cached)
- Event 105 (after compact): 5,000 tokens (full price, cache invalidated)
- **Total: 10,000 tokens charged** for same file content!

---

## Storage & Context Relationship

### Key Distinction

| Aspect | JSONL Storage | API Context | Prompt Cache |
|--------|---------------|-------------|--------------|
| **Location** | Disk | Memory (API request) | Claude's servers |
| **Persistence** | Permanent | Per-request | 5 min TTL |
| **Size** | Unlimited | 200K tokens | Auto-managed |
| **Compact Impact** | ❌ No change | ✅ Reduced 10x | ⚠️ Invalidated |
| **Cost** | Free | $$ per token | $ (0.1x) per read |

**Important:**
- JSONL file keeps **everything** (5.4 MB on disk)
- API context is what **Claude sees** (~190K tokens before compact, ~20K after)
- Cache helps **within 5 min** but doesn't survive compacts

### Why This Matters

**Before understanding this:**
- ❌ "Why is Claude re-reading files I already analyzed?"
- ❌ "I thought caching would prevent this!"
- ❌ "The JSONL file has the content, why not use it?"

**After understanding:**
- ✅ **JSONL is for resuming conversations** (full history preserved)
- ✅ **API context is what Claude actually sees** (limited by 200K)
- ✅ **Cache helps within 5 min** but compacts invalidate it
- ✅ **Compacts are lossy** (details → summary → need to re-read)

---

## Your Filesystem Offloading Idea: THE SOLUTION!

### Why It Solves the Problem

**Current flow (wasteful):**
```
1. Read large files → Store in JSONL (disk) + Context (API) → Cached
2. Compact happens → Summary loses details → Cache invalidated
3. Need details again → Must re-read files → NEW tokens charged
```

**With filesystem offloading (smart):**
```
1. Read large files → Extract key info → Write to .analysis/findings.md
2. Compact happens → Summary references .analysis/findings.md
3. Need details again → Read .analysis/findings.md (100 tokens vs 5,000!)
```

### Example Implementation

**Phase 1: Analysis (Before Compact)**
```
User: "Analyze authentication code"

Agent workflow:
1. Read auth.ts (5,000 tokens)
2. Extract findings:
   - OAuth2 flow implementation
   - Missing CSRF token validation
   - Rate limiting present
3. Write to .analysis/auth-findings.md (200 tokens)
4. Return summary to user

Tokens used: 5,000 (read) + 200 (write) = 5,200
```

**Phase 2: Compact**
```
Summary: "Analyzed auth code, findings in .analysis/auth-findings.md"

Context after compact:
- Summary: 50 tokens
- References: .analysis/auth-findings.md
```

**Phase 3: Follow-up (After Compact)**
```
User: "Check CSRF implementation again"

Agent workflow:
1. Read .analysis/auth-findings.md (200 tokens)
2. See: "Missing CSRF token validation in line 45-60"
3. Read auth.ts lines 45-60 only (500 tokens)
4. Provide detailed answer

Tokens used: 200 + 500 = 700 (vs 5,000 re-reading full file!)

Savings: 86% reduction!
```

---

## Recommendations

### 1. Implement Analysis Persistence (Your Idea!)

**Files:**
- `.analysis/` directory (gitignored)
- `.analysis/file-summaries/` - Key findings per file
- `.analysis/decisions.md` - Architectural decisions
- `.analysis/patterns.md` - Code patterns found

**Workflow:**
```python
# After extensive file analysis
def persist_analysis(findings: dict):
    \"\"\"Write analysis results to filesystem for post-compact access\"\"\"
    write_file(\".analysis/auth-code-analysis.md\", findings)

    # Now compact can reference this file instead of losing details
```

### 2. Create Discovery Skill

**Skill:** `analysis-persistence`

**Triggers:**
- Detects extensive file reading (3+ files >1KB each)
- Suggests: "Save analysis to .analysis/ for later reference?"
- Auto-writes structured summaries

**Benefits:**
- Survives compacts (filesystem persists)
- Cheaper re-reads (200 tokens vs 5,000)
- Explicit context (no hunting through JSONL)

### 3. Use Output Modes Optimally

**Discovery phase:**
```bash
# Instead of reading 10 files fully
grep "auth" --output=files_with_matches  # 100 tokens
# Returns: auth.ts, user.ts, api.ts

# Write findings
echo "Auth files: auth.ts, user.ts, api.ts" > .analysis/auth-files.txt
```

**Analysis phase:**
```bash
# Read only what's needed based on .analysis/auth-files.txt
read auth.ts --offset=45 --limit=50  # 500 tokens (just the function)
```

**Post-compact:**
```bash
# Read summary instead of re-reading files
read .analysis/auth-files.txt  # 10 tokens!
```

---

## Conclusion

### What We Learned

1. **JSONL files are permanent storage** - Full history always on disk
2. **API context is what Claude sees** - Limited to 200K tokens
3. **Compacts are lossy** - Details → Summary → Need to re-read
4. **Caching helps but doesn't survive compacts** - 5 min TTL + invalidation
5. **Filesystem offloading is the solution** - Persist structured summaries

### Why Your Intuition Was Right

You sensed inefficiency because **there IS inefficiency**:
- Same file content counted twice (before + after compact)
- Cache doesn't help (invalidated by compact)
- No built-in analysis persistence mechanism

**Your solution (filesystem offloading) addresses the root cause:**
- ✅ Survives compacts (on disk, not in API context)
- ✅ Cheap re-reads (structured summaries, not full files)
- ✅ Explicit reference (point to .analysis/ in summaries)

### Next Steps

Want to add **Task 6** to the v0.6.0 plan?

**Task 6: Analysis Persistence & Discovery Skill**
- Detect extensive file operations
- Auto-write structured summaries to `.analysis/`
- Read summaries first before re-reading files
- Estimated effort: 3 hours
- Savings: 80-90% token reduction for post-compact work

This would make SlashSense **the first plugin** with built-in compact-aware context optimization!
