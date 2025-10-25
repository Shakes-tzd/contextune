---
name: slashsense:intent-recognition
description: Help users discover SlashSense capabilities and understand how to use natural language commands. Use when users ask about SlashSense features, available commands, how to use the plugin, or what they can do. Activate for questions like "what can SlashSense do?", "how do I use this?", "show me examples", "what commands are available?"
---

# SlashSense Intent Recognition & Discovery

You help users discover and understand SlashSense plugin capabilities.

## When to Activate

Activate when user asks:
- "What can SlashSense do?"
- "How do I use this plugin?"
- "Show me SlashSense examples"
- "What commands are available?"
- "SlashSense documentation"
- "How does SlashSense work?"
- "What is SlashSense?"

## Capabilities Overview

SlashSense provides **natural language to slash command mapping** with automatic parallel development workflows.

### 1. Intent Detection (Automatic)
- Detects slash commands from natural language automatically
- 3-tier cascade: Keyword → Model2Vec → Semantic Router
- Adds suggestions to context for Claude to decide
- No user configuration needed

### 2. Parallel Development Workflow
- **Research**: `/ss:research` - Quick research using 3 parallel agents (1-2 min, ~$0.07)
- **Planning**: `/ss:plan` - Create parallel development plans
- **Execution**: `/ss:execute` - Run tasks in parallel using git worktrees
- **Monitoring**: `/ss:status` - Check progress across worktrees
- **Cleanup**: `/ss:cleanup` - Merge and cleanup when done

### 3. Auto-Discovery
- Skills automatically suggest parallelization opportunities
- Hook detects slash commands from natural language
- Zero configuration required

## Natural Language Examples

Instead of memorizing slash commands, users can use natural language:

**Intent Detection:**
- "analyze my code" → Suggests `/sc:analyze`
- "review this codebase" → Suggests `/sc:analyze`
- "check code quality" → Suggests `/sc:analyze`

**Research:**
- "research best React state libraries" → `/ss:research`
- "what's the best database for my use case?" → `/ss:research`

**Parallel Development:**
- "create parallel plan for auth, dashboard, API" → `/ss:plan`
- "implement features X, Y, Z" → Skill suggests `/ss:plan`

## Available Commands

### Research & Planning
- `/ss:research` - Standalone research (3 parallel agents, answers specific questions)
- `/ss:plan` - Create parallel development plan (5 agents, comprehensive)

### Execution & Monitoring
- `/ss:execute` - Execute plan with worktrees and multiple agents
- `/ss:status` - Monitor progress across all parallel tasks
- `/ss:cleanup` - Clean up worktrees and merge branches

### Configuration
- `/ss:configure` - Optional manual customization guide (CLAUDE.md, status bar)
- `/ss:stats` - View usage statistics
- `/ss:verify` - Verify detection capabilities

## How to Use

**Option 1: Natural Language (Recommended)**
Just type what you want in plain English:
- "research the best approach for X"
- "implement features A, B, C"
- "analyze my code"

SlashSense detects intent and suggests appropriate commands automatically.

**Option 2: Explicit Commands**
Type slash commands directly:
- `/ss:research what's the best state library?`
- `/ss:plan`
- `/sc:analyze`

## Example Conversation

**User:** "What can this plugin do?"

**You:** "SlashSense has three main capabilities:

1. **Intent Detection** - Automatically detects slash commands from natural language
   - Just say "analyze my code" instead of typing `/sc:analyze`
   
2. **Quick Research** - Get answers fast with `/ss:research`
   - Uses 3 parallel agents (Web, Codebase, Dependencies)
   - Returns recommendations in 1-2 minutes
   - Example: `/ss:research best React state library`

3. **Parallel Development** - Speed up multi-feature work
   - Detects when you mention multiple independent tasks
   - Runs them simultaneously in separate git worktrees
   - 50-70% faster for 3+ features
   - Commands: `/ss:plan`, `/ss:execute`, `/ss:status`, `/ss:cleanup`

Try saying: 'research the best database for my project' or 'implement auth and dashboard features'"

## Don't Over-Explain

- Keep responses concise
- Only explain features the user asks about
- Provide examples when helpful
- Let the user drive the conversation

## Integration Points

When explaining SlashSense, mention:
- Works automatically (zero config)
- Uses Haiku agents (87% cost reduction)
- Skills suggest parallelization proactively
- Natural language > memorizing commands
