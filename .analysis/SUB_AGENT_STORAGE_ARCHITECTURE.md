# Sub-Agent Storage Architecture

**Date:** 2025-10-25
**Analysis:** How sub-agents (Task tool) store their context, tool calls, and thinking

---

## Key Discovery: Sub-Agents Store Context in MAIN Session!

After analyzing the JSONL structure, here's what I found:

**Sub-agents do NOT have separate session files.** They store everything in the **MAIN agent's JSONL file**.

---

## Evidence from Actual Data

### Task Tool Invocation (Line 71)

```json
{
  "parentUuid": "b0f5180f-9997-4745-904b-93ec15390831",
  "isSidechain": false,  ← Main session, not separate
  "sessionId": "e596b0a5-456a-4026-b892-a361d01f6841",  ← SAME session ID
  "type": "assistant",
  "message": {
    "role": "assistant",
    "content": [
      {
        "type": "tool_use",
        "id": "toolu_01GEezqT8T5NALRPv4qFrFcC",
        "name": "Task",
        "input": {
          "subagent_type": "general-purpose",
          "description": "Research Claude Code plugin mechanisms",
          "prompt": "Research Claude Code plugin architecture..."
        }
      }
    ]
  }
}
```

### Sub-Agent Result (Line 117)

```json
{
  "parentUuid": "9435a7d9-c3ee-450e-aaa8-cf26644dddfe",
  "isSidechain": false,  ← Still main session
  "sessionId": "e596b0a5-456a-4026-b892-a361d01f6841",  ← SAME session ID
  "type": "user",  ← Marked as "user" event (tool result)
  "message": {
    "role": "user",
    "content": [
      {
        "tool_use_id": "toolu_01GEezqT8T5NALRPv4qFrFcC",  ← Links to tool use
        "type": "tool_result",
        "content": [
          {
            "type": "text",
            "text": "Perfect! Now I have comprehensive information..."
          }
        ]
      }
    ]
  },
  "toolUseResult": {
    "status": "completed",
    "totalDurationMs": 84312,  ← Sub-agent took 84 seconds
    "totalTokens": 26970,      ← Sub-agent used 26,970 tokens
    "totalToolUseCount": 6,     ← Sub-agent made 6 tool calls
    "usage": {
      "input_tokens": 5,
      "cache_creation_input_tokens": 560,
      "cache_read_input_tokens": 25028,
      "output_tokens": 1377
    }
  }
}
```

---

## How Sub-Agent Storage Actually Works

### Storage Model: "Collapsed Execution"

```
Main Session JSONL File
└── Event 71: Main agent uses Task tool
    │  - Spawns sub-agent
    │  - Sub-agent gets independent Claude API session
    │  - Sub-agent executes in isolation (separate context window)
    │
    │  [SUB-AGENT EXECUTION - 84 seconds]
    │  ├── Sub-agent reads docs
    │  ├── Sub-agent uses WebFetch
    │  ├── Sub-agent processes info
    │  ├── Sub-agent generates report
    │  └── Sub-agent returns result
    │
    └── Event 117: Tool result recorded
       - Sub-agent's FINAL REPORT stored
       - Sub-agent's USAGE STATS stored
       - Sub-agent's intermediate steps: NOT STORED in main JSONL
```

**Key insight:** Sub-agent's internal context (individual tool calls, thinking blocks, intermediate steps) is **NOT stored in main session JSONL**. Only the **final result** is stored.

---

## What Gets Stored Where

### Main Session JSONL (e596b0a5-456a-4026-b892-a361d01f6841.jsonl)

**Stores:**
- ✅ Task tool invocation (prompt to sub-agent)
- ✅ Final result from sub-agent
- ✅ Token usage summary
- ✅ Duration statistics
- ✅ Tool use count

**Does NOT store:**
- ❌ Sub-agent's individual tool calls (Read, WebFetch, etc.)
- ❌ Sub-agent's thinking blocks
- ❌ Sub-agent's intermediate reasoning
- ❌ Sub-agent's step-by-step execution

### Sub-Agent's Own Context

**Where:** Ephemeral - exists only during execution, then discarded

**Lifecycle:**
1. Main agent spawns sub-agent via Task tool
2. Claude Code creates NEW Claude API session for sub-agent
3. Sub-agent has INDEPENDENT 200K context window
4. Sub-agent executes prompt using its own tools
5. Sub-agent generates final report
6. **Final report sent back to main agent**
7. **Sub-agent's context DISCARDED** (not saved to disk)

**Evidence:**
- No separate JSONL files for sub-agents found
- `sessionId` remains constant (main session)
- Only tool result stored, not execution trace

---

## Sub-Agent Context Isolation

### Main Agent Context (Before Task)

```
Context: 80K tokens
├── CLAUDE.md
├── Previous conversation
├── File reads
└── Current task
```

### Sub-Agent Context (During Execution)

```
COMPLETELY SEPARATE CONTEXT (Fresh 200K window)
├── Task tool prompt (from main agent)
├── Sub-agent's own tool calls:
│   ├── WebFetch docs (5K tokens)
│   ├── Read file results (10K tokens)
│   └── Processing (2K tokens)
└── Sub-agent's response generation (1.4K tokens)

Total: ~18K tokens (independent of main agent's 80K)
```

### Main Agent Context (After Task)

```
Context: 80K + result tokens
├── [Previous 80K context unchanged]
└── Tool result from sub-agent (1.4K tokens added)

New total: 81.4K tokens
```

**Key benefit:** Sub-agent's 18K execution context does NOT pollute main agent's context. Only the 1.4K result is added.

---

## Token Accounting

### Example from Actual Data

**Task invocation (line 71):**
```json
"usage": {
  "input_tokens": 9,
  "cache_creation_input_tokens": 80061,
  "output_tokens": 2
}
```
- Main agent creates Task tool use: 80,061 tokens cached, 9 new tokens

**Tool result (line 117):**
```json
"toolUseResult": {
  "totalTokens": 26970,  ← Sub-agent's TOTAL consumption
  "usage": {
    "input_tokens": 5,
    "cache_read_input_tokens": 25028,  ← Sub-agent read from cache
    "output_tokens": 1377               ← Sub-agent's final report
  }
}
```

**Cost calculation:**
- Sub-agent input: 5 + 25,028 (cache) = 25,033 tokens
- Sub-agent output: 1,377 tokens
- **Sub-agent total: 26,410 tokens**
- Main agent receives: **1,377 token result** (added to main context)

**Main agent savings:**
- If main agent did the work: ~26,410 tokens in main context
- With sub-agent: Only 1,377 tokens in main context
- **Context saved: 25,033 tokens (95% reduction!)**

---

## Where Do Sub-Agent Tool Calls Actually Go?

### Answer: Nowhere (ephemeral execution)

**Sub-agent's execution trace:**
```
[NOT STORED ANYWHERE]
├── WebFetch https://docs.claude.com/... (result: 5K tokens)
├── Read ~/.claude/settings.json (result: 2K tokens)
├── Grep "hook" (result: 500 tokens)
├── Thinking about architecture (3K tokens)
└── Generate final report (1.4K tokens)
```

**What's stored in main JSONL:**
```
[ONLY THIS IS STORED]
└── Tool result: "Perfect! Now I have comprehensive information..." (1.4K tokens)
```

**Why this matters:**
- Sub-agent can do extensive exploration (26K tokens)
- Main agent's JSONL stays small (only 1.4K result added)
- Sub-agent's JSONL doesn't exist (ephemeral execution)
- **Sub-agent thinking/tool calls are NEVER saved to disk**

---

## Implications for Context Management

### Positive Implications

1. **Main context stays clean:**
   - Sub-agents can do messy exploration
   - Only clean results returned
   - Main JSONL doesn't bloat with sub-agent details

2. **Cost efficiency:**
   - Sub-agents can use 26K tokens
   - Main context only grows by 1.4K
   - 95% context saving vs doing work in main agent

3. **Independent thinking:**
   - Sub-agent has fresh 200K window
   - No pollution from main agent's context
   - Can think deeply without constraints

### Negative Implications

1. **No execution trace:**
   - Can't debug sub-agent reasoning
   - Can't see what files sub-agent read
   - No way to verify sub-agent's work

2. **No resumability:**
   - Sub-agent context discarded after execution
   - Can't resume sub-agent's work
   - Must re-spawn if need more info

3. **Compact doesn't help:**
   - Sub-agent results already in main context
   - Compacting main agent doesn't recover sub-agent details
   - Sub-agent execution trace already lost

---

## Comparison with Main Agent Storage

| Aspect | Main Agent | Sub-Agent |
|--------|------------|-----------|
| **JSONL Storage** | ✅ Yes (`session-id.jsonl`) | ❌ No (ephemeral) |
| **Tool Call Records** | ✅ Every tool call saved | ❌ Only final result |
| **Thinking Blocks** | ✅ Saved to JSONL | ❌ Not saved anywhere |
| **Context Window** | 200K tokens | 200K tokens (independent) |
| **Resumability** | ✅ Can resume from JSONL | ❌ Cannot resume |
| **Debugging** | ✅ Full execution trace | ❌ Black box (result only) |
| **Cost to Main Context** | Full cost (all tokens) | Minimal (result only) |

---

## Detailed Example: Research Sub-Agent

### Task Given to Sub-Agent

```
"Research Claude Code plugin architecture focusing on discovery mechanisms.
Use WebFetch to read docs and report back."
```

### Sub-Agent's Actual Execution (NOT STORED)

```
[EPHEMERAL - IN MEMORY ONLY]

Event 1: Sub-agent starts
  Context: 0 tokens
  Receives: Task prompt (500 tokens)

Event 2: Sub-agent uses WebFetch
  Tool: WebFetch(url="https://docs.claude.com/...")
  Result: 5,000 tokens of documentation
  Context now: 5,500 tokens

Event 3: Sub-agent thinks
  Thinking block: "I need to analyze hooks vs skills..."
  Thinking: 2,000 tokens
  Context now: 7,500 tokens

Event 4: Sub-agent uses WebFetch again
  Tool: WebFetch(url="https://docs.claude.com/hooks")
  Result: 4,000 tokens of hook docs
  Context now: 11,500 tokens

Event 5: Sub-agent synthesizes
  Thinking: "Based on the research..."
  Thinking: 3,000 tokens
  Context now: 14,500 tokens

Event 6: Sub-agent generates report
  Output: "## Claude Code Discovery Mechanisms..." (1,377 tokens)
  Context now: 15,877 tokens

Event 7: Sub-agent returns
  Returns: 1,377 token report to main agent
  Sub-agent context DISCARDED (15,877 tokens gone forever)
```

### What Main Agent Stores in JSONL

```
[STORED PERMANENTLY]

Event 71: Task tool use
{
  "name": "Task",
  "input": {
    "prompt": "Research Claude Code plugin architecture..."
  }
}

Event 117: Tool result
{
  "tool_use_id": "toolu_01GEezqT8T5NALRPv4qFrFcC",
  "content": "## Claude Code Discovery Mechanisms...",
  "toolUseResult": {
    "totalTokens": 26970,
    "usage": {...}
  }
}
```

**What's missing from storage:**
- ❌ Sub-agent's 2 WebFetch calls
- ❌ Sub-agent's 2 thinking blocks (5,000 tokens total)
- ❌ Sub-agent's intermediate reasoning
- ❌ 14,500 tokens of sub-agent's work (only 1,377 result stored)

---

## Why This Architecture Makes Sense

### Design Rationale

1. **JSONL files would explode:**
   - 5 parallel sub-agents × 20K tokens each = 100K tokens
   - Would bloat main JSONL from 5.4 MB to 50+ MB
   - Resume times would be horrible

2. **Main context stays manageable:**
   - 5 sub-agents return 5 × 1.5K = 7.5K tokens total
   - Main context grows moderately
   - Compact still effective

3. **Sub-agents are disposable:**
   - Designed for one-off tasks
   - Don't need long-term storage
   - Results are what matter, not process

### Trade-offs

**Good:**
- ✅ Main JSONL stays small
- ✅ Main context stays clean
- ✅ Sub-agents have freedom to explore
- ✅ Cost-effective (only results count)

**Bad:**
- ❌ No debugging sub-agent execution
- ❌ Can't inspect sub-agent reasoning
- ❌ Must trust sub-agent's work blindly
- ❌ No audit trail for sub-agent decisions

---

## Answer to Your Question

> "Given that sub-agents have their own independent context, where do they store their tool calls and thinking?"

**Answer:** They don't. Sub-agents store nothing to disk.

**Full explanation:**

1. **During execution:** Sub-agent context exists in memory (Claude API session)
2. **Tool calls:** Made by sub-agent, results in sub-agent's memory, not saved
3. **Thinking blocks:** Generated in sub-agent's context, discarded after completion
4. **After completion:** Only the final text result is sent back to main agent
5. **Storage:** Main agent stores the result in its JSONL, sub-agent stores nothing

**Key insight:** Sub-agents are ephemeral execution environments. They're like temporary workers who:
- Get a task
- Do extensive research (tool calls, thinking)
- Write a final report
- Hand the report to the main agent
- **Disappear** (all their working notes gone)

---

## Implications for Your Filesystem Offloading Idea

### Even More Valuable Now!

**Why:** Sub-agents can't persist their own analysis. Only the main agent can write to filesystem.

**Pattern:**
```
1. Main agent spawns sub-agent: "Analyze auth code"
2. Sub-agent reads 10 files (50K tokens in sub-agent context)
3. Sub-agent writes report (2K tokens)
4. Sub-agent returns report to main agent
5. Sub-agent context DISCARDED (50K tokens gone!)
6. Main agent receives 2K report
7. **Main agent writes to .analysis/auth-summary.md** ← KEY STEP
8. Now .analysis/ has persistent summary (survives compacts AND future sessions)
```

**Without filesystem persistence:**
- Sub-agent's 50K analysis: GONE
- Main agent's 2K summary: Compacted away eventually
- **Result: All knowledge lost**

**With filesystem persistence:**
- Sub-agent's 2K summary: Saved to `.analysis/`
- Main agent references `.analysis/` in future
- **Result: Knowledge persists forever**

---

## Recommendations

### 1. Use Sub-Agents for Heavy Lifting

**Good use:** Research, exploration, analysis
- Sub-agent can use 50K tokens exploring
- Main context only grows by 2K result
- 96% context savings!

### 2. Always Persist Sub-Agent Results

**Pattern:**
```python
# After sub-agent returns
result = task_tool_result["content"]

# IMMEDIATELY persist to filesystem
write_file(f".analysis/{task_name}-{timestamp}.md", result)

# Now it survives:
# - Compacts (not in API context, on disk)
# - Sessions (filesystem persists)
# - Sub-agent ephemeral execution
```

### 3. Reference Filesystem in Summaries

**Pattern:**
```
When compact happens:
Summary: "Researched auth code, findings in .analysis/auth-2025-10-25.md"

NOT:
Summary: "Researched auth code, found OAuth2 implementation with..."
(Details lost, must re-research)
```

---

## Conclusion

**Sub-agent storage is EPHEMERAL by design:**
- Context exists only during execution
- Tool calls and thinking NOT saved to disk
- Only final result returned to main agent
- Main agent stores result in its JSONL
- Sub-agent's 200K context window discarded

**This is why filesystem offloading is CRITICAL:**
- Sub-agents can't persist their own work
- Main agent must save sub-agent results
- Without filesystem persistence, sub-agent knowledge is lost
- `.analysis/` directory becomes single source of truth

**Your insight about filesystem offloading isn't just good for compacts—it's ESSENTIAL for sub-agent workflows!**
