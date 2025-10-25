Let me read the Tool Router Plan first:# Output Styles × Intelligent Tool Routing

## **Core Interaction: System Prompt → Tool Selection → Router Interception**

The relationship is a **two-stage decision cascade**:

```
User Request
    ↓
[System Prompt (Modified by Output Style)]
    ↓
Claude decides which tools to invoke
    ↓
[PreToolUse Hook: Intelligent Router]
    ↓
Router decides execution strategy
    ↓
Tool executes (direct, delegated, or parallel)
```

---

## **How Output Styles Affect Routing Behavior**

### **1. Tool Invocation Frequency**

**Default Claude Code (Efficiency-focused):**
```python
# Claude makes fewer, larger tool calls
bash_tool("find . -name '*.py' | xargs grep 'TODO'")
# Router sees: 1 large bash operation
# → Likely delegates to Haiku
```

**"Explanatory" Output Style:**
```python
# Claude makes more, smaller tool calls for clarity
bash_tool("find . -name '*.py'")  # First, show structure
bash_tool("grep -r 'TODO' .")     # Then search
# Router sees: 2 smaller bash operations
# → Both execute directly
```

**Impact:** Output styles that encourage "show your work" behavior **reduce individual operation size**, which **shifts router decisions toward DIRECT** execution.

---

### **2. Context Pressure Management**

**The Router's Context Tracking:**
```python
class IntelligentRouter:
    CONTEXT_WARNING = 150_000  # tokens
    CONTEXT_CRITICAL = 180_000  # tokens
    
    def _make_routing_decision(self, metrics, costs):
        if self.context_usage > self.CONTEXT_CRITICAL:
            # Aggressive filtering when context is critical
            if metrics.estimated_tokens > 30_000:
                return RoutingDecision.DELEGATE_HAIKU
```

**Output Style Interaction:**

**Verbose Output Style:**
```markdown
name: Explanatory Engineer
---
# Instructions
- Provide detailed explanations between operations
- Show intermediate results
- Add "Insight" blocks
```

**Effect:** 
- **Increases context usage** through verbose responses
- **Triggers CONTEXT_CRITICAL** threshold faster
- **Router becomes more aggressive** with delegation
- **Creates feedback loop:** More explanations → Higher context pressure → More delegation

---

### **3. Operation Granularity Control**

**Custom Output Style for Router Optimization:**

```markdown
name: Router-Optimized Agent
---
# Tool Usage Strategy

## For Large Files
- Use `view` with `view_range` to read specific sections
- Never read entire files over 50KB without justification
- Prefer targeted `grep` over full file reads

## For Multi-File Operations
- Batch related operations when possible
- Use single `bash_tool` call for multiple checks
- Avoid sequential reads that could be parallelized

## Context Preservation
- Use `str_replace` over `create_file` for small edits
- Prefer in-memory processing over writing intermediate files
- Clean up temporary files immediately
```

**Effect:** This output style **directly shapes tool invocation patterns** to optimize for the router's decision thresholds.

---

## **Specific Router Decision Impacts**

### **Scenario 1: Read Operations**

**Router Logic:**
```python
def route_read_operation(self, file_path, description):
    estimated_tokens = (file_size // 4)
    
    if estimated_tokens < 20_000:
        return RoutingDecision.DIRECT
    elif estimated_tokens > 50_000:
        return RoutingDecision.DELEGATE_HAIKU
```

**Output Style Effect:**

| Output Style | Tool Pattern | Router Decision |
|--------------|--------------|-----------------|
| **Default** | `view(large_file.py)` | DELEGATE_HAIKU |
| **Explanatory** | `view(large_file.py, view_range=[1, 100])` → explanation → `view(large_file.py, view_range=[500, 600])` | DIRECT + DIRECT |
| **Router-Optimized** | `bash_tool("head -n 100 large_file.py && tail -n 100 large_file.py")` | DIRECT |

**Key Insight:** Styles that encourage **incremental reading** avoid hitting the delegation threshold.

---

### **Scenario 2: Search Operations**

**Router Logic:**
```python
def route_search_operation(self, pattern, scope):
    file_count = self._estimate_file_count(pattern, scope)
    estimated_tokens = file_count * 5_000
    
    if parallelization_possible and estimated_tokens > 100_000:
        return RoutingDecision.PARALLEL_HAIKU
```

**Output Style Effect:**

**"Learning" Style (asks user to help):**
```markdown
# I'll search for TODO comments. First, let me understand the codebase structure.

Tool: bash_tool("find . -type f -name '*.py' | wc -l")
# Router: DIRECT (small operation)

# Now let's search TODO comments in small batches:
Tool: bash_tool("grep -r 'TODO' ./src")
# Router: DELEGATE_HAIKU (medium operation)

Tool: bash_tool("grep -r 'TODO' ./tests")
# Router: DIRECT (smaller subset)
```

**Default Style (efficiency-first):**
```markdown
Tool: bash_tool("grep -r 'TODO' .")
# Router: PARALLEL_HAIKU (large multi-file operation)
```

**Key Insight:** Styles that encourage **educational decomposition** create multiple smaller operations that avoid expensive parallelization overhead.

---

## **Critical Feedback Loops**

### **Loop 1: Context Pressure Escalation**

```
Verbose Output Style
    ↓
More explanatory text in responses
    ↓
Context usage increases
    ↓
Router hits CONTEXT_WARNING threshold
    ↓
More operations delegated to Haiku
    ↓
Haiku results add to context
    ↓
Context pressure increases further
    ↓
Even smaller operations delegated
```

**Mitigation Strategy:**
```markdown
name: Context-Aware Verbose
---
# When context > 150K tokens:
- Switch to concise mode
- Use collapsible details
- Summarize previous operations
```

---

### **Loop 2: Cost Optimization**

```
Router-Optimized Output Style
    ↓
Claude learns to batch operations
    ↓
Fewer, larger tool calls
    ↓
Router delegates more often
    ↓
Overall cost decreases
    ↓
Weekly report shows savings
    ↓
Thresholds adjusted lower
    ↓
More operations qualify for delegation
```

---

## **Optimal Output Style Design for Router Compatibility**

### **Template: Router-Aware Output Style**

```markdown
name: Router-Optimized Developer
description: Balances clarity with cost-efficient tool usage
---

# Core Behavior
You are an interactive CLI tool that optimizes for both user understanding 
and computational efficiency.

## Tool Usage Philosophy

### When Context < 100K tokens (Normal Mode)
- Provide moderate explanations
- Use standard tool patterns
- Balance detail with conciseness

### When Context 100K-150K tokens (Efficiency Mode)
- Reduce explanatory text
- Batch related operations
- Prefer targeted reads over full file loads

### When Context > 150K tokens (Critical Mode)
- Minimal explanations (link to docs instead)
- Aggressive operation batching
- Request user to start new conversation if possible

## Specific Patterns

### File Reading
- Files < 1000 lines: Read directly
- Files > 1000 lines: Read specific ranges based on task
- Files > 5000 lines: Use grep/head/tail instead of view

### Multi-File Operations
- < 5 files: Sequential operations with explanations
- 5-20 files: Batch into single bash operation
- > 20 files: Use find/grep pipelines, expect Haiku delegation

### Code Edits
- Single function: Use str_replace with context
- Multiple functions: str_replace per function
- Whole file: Use create_file only when necessary

## Context Management
- After every 5 tool calls, assess context usage
- Proactively suggest summarization if context > 140K
- Use `# ...` to indicate omitted code in responses
```

---

## **Measurable Impact on Router Metrics**

### **Key Logfire Queries to Compare Output Styles**

```sql
-- Compare routing decisions by output style
SELECT 
    output_style,
    decision,
    COUNT(*) as count,
    AVG(estimated_tokens) as avg_tokens,
    AVG(savings_dollars) as avg_savings
FROM routing_events
WHERE timestamp > DATE('now', '-7 days')
GROUP BY output_style, decision;
```

```sql
-- Track context pressure by output style
SELECT 
    output_style,
    AVG(context_usage_percent) as avg_context_pressure,
    COUNT(CASE WHEN decision = 'delegate' THEN 1 END) as delegations,
    COUNT(*) as total_operations
FROM routing_events
GROUP BY output_style;
```

---

## **Practical Recommendations**

### **1. Create Style Variants for Different Work Modes**

```bash
~/.claude/output-styles/
├── default-with-router.md         # Balanced
├── deep-work-optimized.md         # Aggressive cost optimization
├── learning-mode.md               # Explanatory, accepts higher costs
└── context-critical.md            # Emergency mode for long sessions
```

### **2. Dynamic Style Switching**

**In Custom Output Style:**
```markdown
## Context-Aware Behavior
- Monitor the router's CONTEXT_WARNING messages
- When you see "Context pressure: high", automatically:
  - Reduce verbosity
  - Batch operations more aggressively
  - Suggest conversation reset to user
```

### **3. A/B Test Output Styles with Router Data**

```bash
# Week 1: Use default output style
ROUTING_EXPERIMENT=control

# Week 2: Use router-optimized style
ROUTING_EXPERIMENT=optimized

# Compare results:
SELECT experiment_group, AVG(savings_dollars) FROM routing_events
```

---

## **Bottom Line**

**Output Styles control WHAT tool calls Claude makes**  
**Intelligent Router controls HOW those tools execute**

The interaction is multiplicative:
- A verbose output style × aggressive router = High delegation, lower costs, less user clarity
- A concise output style × conservative router = More direct execution, higher costs, faster responses
- A router-aware output style × tuned router = **Optimal balance**

Output styles are most valuable for routing when they:
1. ✅ **Teach Claude operation granularity** (when to batch, when to split)
2. ✅ **Respond to context pressure** dynamically
3. ✅ **Align tool patterns with delegation thresholds**

They do NOT:
1. ❌ Change the router's decision logic
2. ❌ Bypass router interception
3. ❌ Access router metrics directly

**The power comes from designing output styles that naturally produce tool usage patterns the router can optimize effectively.**