# SlashSense Delegation Modes

SlashSense now supports three delegation modes that control how detected commands are handled, including a **sub-agent verification mode** that preserves your main agent's context.

## Overview

| Mode | Behavior | Context Usage | Safety | Speed |
|------|----------|---------------|--------|-------|
| **verify** | Spawns sub-agent to ask user | Minimal | ✅ Safest | ⚡⚡ Fast |
| **suggest** | Adds context, main agent decides | Moderate | ✅ Safe | ⚡⚡ Fast |
| **auto** | Auto-executes detected command | None | ⚠️ Risky | ⚡⚡⚡ Fastest |

## Verify Mode (Recommended)

**How it works:**
```
User types: "analyze my code"
    ↓
Hook detects: /sc:analyze
    ↓
Main agent receives delegation directive
    ↓
Main agent spawns sub-agent
    ↓
Sub-agent asks user: "Option 1: /sc:analyze or Option 2: original prompt?"
    ↓
Sub-agent executes user's choice
    ↓
Sub-agent reports back to main agent
    ↓
Main agent context preserved!
```

**Benefits:**
- ✅ **User verification** - You confirm before execution
- ✅ **Context preservation** - Main agent doesn't waste tokens
- ✅ **Safe** - No unexpected command execution
- ✅ **Flexible** - You can choose original prompt or detected command

**Example Flow:**

```
You: "can you help me analyze this code for bugs"

Claude (Main): 🎯 SlashSense detected a command. Spawning verification agent...

[Sub-agent spawned]

Claude (Sub-agent):
🎯 **SlashSense Detection**

I detected you might want to run a slash command:

**Option 1**: Run `/sc:analyze` (85% confidence)
**Option 2**: Continue with original: "can you help me analyze this code for bugs"

Which do you prefer? (1, 2, or tell me what you want)

You: 1

Claude (Sub-agent):
✅ Executing /sc:analyze...

[Performs analysis]

**SlashSense Verification Complete**
User choice: Option 1 (/sc:analyze)
Action taken: Ran code analysis
Result: Found 3 potential issues

[Returns to main agent]

Claude (Main): [continues with minimal context consumed]
```

## Suggest Mode

**How it works:**
```
User types: "analyze my code"
    ↓
Hook detects: /sc:analyze
    ↓
Main agent receives: original prompt + suggestion
    ↓
Main agent asks user which they prefer
    ↓
Main agent executes
```

**Benefits:**
- ✅ User verification
- ⚡ Slightly faster (no sub-agent spawn)
- ⚠️ Uses main agent context for verification

**When to use:**
- You want verification but don't care about context usage
- Quick one-off tasks

## Auto Mode (Original Behavior)

**How it works:**
```
User types: "analyze my code"
    ↓
Hook detects: /sc:analyze
    ↓
Main agent receives: "/sc:analyze" (original prompt replaced!)
    ↓
Executes immediately
```

**Benefits:**
- ⚡⚡⚡ Fastest
- No interruption

**Risks:**
- ❌ No verification
- ❌ Original prompt context lost
- ❌ Wrong detections execute immediately

**When to use:**
- You trust the detection 100%
- High-confidence scenarios only
- You understand the risks

## Configuration

### Set Delegation Mode

Edit `~/.claude/plugins/slashsense/data/user_patterns.json`:

```json
{
  "enabled": true,
  "confidence_threshold": 0.7,
  "delegation_mode": "verify",  // ← Change this
  "tiers": {
    "keyword": true,
    "model2vec": true,
    "semantic_router": true
  }
}
```

**Options:**
- `"verify"` - Sub-agent verification (recommended)
- `"suggest"` - Main agent asks
- `"auto"` - Auto-execute

### View Current Configuration

```bash
/slashsense:config
```

## Advanced: Hybrid Mode (Coming Soon)

Future version will support hybrid mode:

```json
{
  "delegation_mode": "hybrid",
  "auto_execute_threshold": 0.95,
  "auto_execute_whitelist": [
    "/sc:analyze",
    "/sc:explain",
    "/slashsense:stats"
  ]
}
```

**Behavior:**
- Confidence ≥ 95% + whitelisted → auto-execute
- Confidence 70-95% → verify mode
- Confidence < 70% → pass through

## Technical Details

### Sub-Agent Architecture

**Main Agent receives:**
```json
{
  "continue": true,
  "hookSpecificOutput": {
    "additionalContext": "[Delegation directive with detection details]"
  },
  "feedback": "🎯 SlashSense: Spawning verification agent"
}
```

**Main Agent spawns sub-agent with:**
```python
Task(
    subagent_type="general-purpose",
    description="Verify SlashSense detection",
    prompt="[Verification instructions with detected command]"
)
```

**Sub-agent:**
1. Presents options to user
2. Waits for user choice
3. Executes chosen action
4. Reports results
5. Exits (context discarded)

**Main agent:**
- Receives brief summary
- Continues with preserved context

### Context Savings

**Without sub-agent delegation:**
```
Main agent tokens: Original prompt (20) + Detection message (50) + User response (10) + Execution (200) = 280 tokens
```

**With sub-agent delegation:**
```
Main agent tokens: Delegation directive (100) + Sub-agent summary (50) = 150 tokens
Sub-agent tokens: Verification (50) + User response (10) + Execution (200) = 260 tokens
Total: 410 tokens (but main agent only uses 150)
```

**Savings:** Main agent uses 46% less context!

## FAQ

**Q: Can I change modes mid-conversation?**
A: Yes! Edit the config file and the next prompt will use the new mode.

**Q: What if I don't want SlashSense at all?**
A: Set `"enabled": false` in config, or uninstall: `/plugin uninstall slashsense`

**Q: Can the sub-agent access my files?**
A: Yes, sub-agents have the same permissions as the main agent.

**Q: What if detection is wrong?**
A: In verify/suggest modes, you choose. In auto mode, you're stuck with it (use verify mode!)

**Q: Does this work with all commands?**
A: Yes, SlashSense detects any slash command it's trained on.

## Recommendations

**For safety:** Use `"verify"` mode
**For speed:** Use `"auto"` mode (but understand the risks)
**For balance:** Use `"suggest"` mode

**Default:** `"verify"` mode is the safest and recommended option.

---

**See also:**
- [Architecture](./architecture.md)
- [Configuration](./configuration.md)
- [Usage Guide](./usage.md)
