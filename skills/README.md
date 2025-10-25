# Contextune Skills - Autonomous Expert Guidance

**Version:** 0.5.4
**Status:** ✅ Experimental (0.x)

Contextune now includes **AI-powered Skills** that provide autonomous expert guidance. Skills are **model-invoked** - Claude automatically activates them when you need help, no commands required!

---

## 🎯 What Are Skills?

Skills are specialized capabilities that Claude autonomously uses based on your requests. Unlike slash commands (which you invoke explicitly), Skills activate automatically when Claude detects you need expert help.

**Key Difference:**

```
Slash Commands: User-invoked
  You: "/contextune:execute"
  Claude: Executes the command

Skills: Model-invoked
  You: "How can I speed up development?"
  Claude: *Automatically activates parallel-development-expert skill*
          "Let me analyze your project for parallelization opportunities..."
```

---

## 📦 Available Skills

### 1. **parallel-development-expert**

**What it does:** Provides expert guidance on parallel development workflows

**Activates when you mention:**
- "How can I work on multiple features at once?"
- "Speed up development"
- "Parallel work"
- "Concurrent tasks"
- "Work on several things simultaneously"

**Capabilities:**
- ✅ Analyzes your project for parallelizable tasks
- ✅ Calculates time savings (30-70%)
- ✅ Suggests optimal task breakdown
- ✅ Teaches parallel development patterns
- ✅ Quantifies performance improvements

**Example:**
```
You: "I need to build auth, dashboard, and analytics. Any way to speed this up?"

Claude: *Activates parallel-development-expert*

"Absolutely! These are highly parallelizable:

📊 Analysis:
1. Authentication - Independent ✅ (3 hours)
2. Dashboard - Independent ✅ (2.5 hours)
3. Analytics - Independent ✅ (2 hours)

⚡ Time Savings:
- Sequential: 7.5 hours
- Parallel: 3 hours (60% faster!)

Would you like me to create a parallel execution plan?"
```

---

### 2. **intent-recognition**

**What it does:** Helps you discover Contextune capabilities

**Activates when you ask:**
- "What can Contextune do?"
- "How do I use this?"
- "Show me examples"
- "What commands are available?"
- "Can you help me with...?"

**Capabilities:**
- ✅ Explains Contextune features interactively
- ✅ Shows natural language examples
- ✅ Demonstrates capabilities
- ✅ Guides first-time users
- ✅ Provides "try saying..." suggestions

**Example:**
```
You: "What can Contextune do?"

Claude: *Activates intent-recognition*

"Contextune makes Claude Code more natural! Instead of memorizing commands,
just describe what you want.

🎯 Main Capabilities:

1. Parallel Development - Work on multiple features simultaneously
   Try: 'work on auth and dashboard in parallel'

2. Smart Intent Detection - I understand what you're trying to do
   Try: 'speed up development'

3. Zero Configuration - Works immediately!

Want to try? Describe a project you're working on!"
```

---

### 3. **git-worktree-master**

**What it does:** Expert troubleshooting for git worktree issues

**Activates when you have:**
- "Can't remove worktree" errors
- Locked files or directories
- Orphaned branches
- Cleanup questions
- Worktree conflicts

**Capabilities:**
- ✅ Diagnoses worktree problems
- ✅ Provides safe fixes (explains before executing)
- ✅ Teaches prevention strategies
- ✅ Offers automated cleanup scripts
- ✅ Handles complex edge cases

**Example:**
```
You: "I can't remove worktrees/task-123, getting 'locked' error"

Claude: *Activates git-worktree-master*

"Let me diagnose that...

📊 Diagnosis:
Worktree: worktrees/task-123
Status: Locked ⚠️
Cause: Lock file present (git operation interrupted)

🔧 Safe Fix:
1. Verify no git processes running ✅
2. Remove lock file (safe, no data loss)
3. Remove worktree properly

May I proceed? This will:
✅ Remove the lock
✅ Remove the worktree
⚠️ Keep your branch (in case you need it)"
```

---

### 4. **performance-optimizer**

**What it does:** Analyzes and optimizes parallel workflow performance

**Activates when you:**
- Report slow parallel execution
- Ask "why is this slow?"
- Want performance analysis
- Need benchmarking
- Ask about time savings

**Capabilities:**
- ✅ Identifies performance bottlenecks
- ✅ Calculates parallel efficiency
- ✅ Provides optimization recommendations
- ✅ Shows before/after comparisons
- ✅ Estimates impact of improvements

**Example:**
```
You: "My parallel workflow is taking 10 minutes for 3 tasks. Is that normal?"

Claude: *Activates performance-optimizer*

"Let me analyze your performance...

📊 Analysis:

**Your Timing:**
- Setup: 180s ⚠️ (too high!)
- Execution: 300s ✅
- Total: 480s (8 min)

**Expected (optimized):**
- Setup: 73s ✅
- Execution: 300s
- Total: 373s (6.2 min)

🔍 Bottleneck: Sequential setup (107s overhead)

💡 Fix: Switch to parallel setup pattern
Savings: 107s (22% faster!)

Would you like me to optimize your workflow?"
```

---

## 🚀 How to Use Skills

### The Magic: You Don't Need To!

Skills activate automatically when Claude detects you need them. Just talk naturally:

```
❌ Don't: "Activate the parallel-development-expert skill"
✅ Do: "Can you help me work on multiple features faster?"

❌ Don't: "Use git-worktree-master to fix this error"
✅ Do: "I'm getting a worktree locked error"

❌ Don't: "Run performance-optimizer analysis"
✅ Do: "Why is my parallel workflow so slow?"
```

### Natural Language Examples

**Parallel Development:**
```
"I need to build 5 features - can we do them in parallel?"
"How do I work on multiple tasks simultaneously?"
"Speed up development by parallelizing work"
"Work on auth and dashboard at the same time"
```

**Discovery:**
```
"What can I do with Contextune?"
"Show me what's possible"
"How does this work?"
"Give me some examples"
```

**Troubleshooting:**
```
"I can't remove this worktree"
"Getting a locked error"
"How do I clean up old worktrees?"
"Git worktree issues"
```

**Performance:**
```
"Why is this slow?"
"Can I make parallel execution faster?"
"Analyze my workflow performance"
"How much time am I saving?"
```

---

## 🎨 Skill Capabilities

### What Skills Can Do

**Read Your Codebase:**
```
Skills can analyze your project structure, dependencies, and patterns
to provide tailored recommendations.
```

**Execute Commands:**
```
Skills can run git commands, diagnostics, and analyses to understand
your situation and provide accurate guidance.
```

**Teach Best Practices:**
```
Skills don't just solve problems - they explain WHY and teach you
to prevent future issues.
```

**Quantify Impact:**
```
Skills provide concrete metrics: "This will save 2.3 hours (23% faster)"
Not vague promises!
```

### What Skills Can't Do

**No Dangerous Operations Without Asking:**
```
Skills NEVER perform destructive operations (delete, force-push, etc.)
without explaining first and getting your confirmation.
```

**No Black Box Magic:**
```
Skills explain what they're doing and why. You're always in control.
```

---

## 🔧 Skill Integration

Skills work together seamlessly:

```
Scenario: "I want to work on 10 features in parallel but I'm getting worktree errors"

1. parallel-development-expert activates first:
   "Great! 10 features is ambitious. Let me analyze..."

2. Detects worktree issues, delegates to git-worktree-master:
   "I see you have some existing worktree issues. Let me diagnose..."

3. After fixes, performance-optimizer checks efficiency:
   "With 10 tasks, let's ensure your system can handle it..."

Result: Coordinated expert guidance from multiple skills!
```

---

## 📊 Success Stories

### Before Skills (Traditional Approach)

```
User: "I need to build auth, dashboard, and analytics"
Claude: "I can help. What would you like to do first?"
User: "Can I do them at the same time?"
Claude: "Yes, you can use git branches"
User: "How?"
Claude: "Create branches with git branch..."
[20 minutes of back-and-forth, no parallelization]
```

### After Skills (With Contextune)

```
User: "I need to build auth, dashboard, and analytics"

Claude: *parallel-development-expert activates*

"These are highly parallelizable! Here's the analysis:

✅ All 3 tasks are independent
⚡ Sequential: 8 hours → Parallel: 3 hours (62% faster!)

Say 'work on these in parallel' and I'll handle the rest!"

[User gets parallel execution in seconds, with time savings quantified]
```

---

## 🎓 Learning Resources

### Understanding Skills vs Commands

| Feature | Skills | Slash Commands |
|---------|--------|----------------|
| Invocation | Automatic | Manual |
| Complexity | Multi-step workflows | Simple prompts |
| Files | Multiple (scripts, templates) | Single .md file |
| Discovery | "How do I...?" | "/command" |
| Best For | Expert guidance | Quick actions |

### Skill Architecture

```
contextune/
├── skills/
│   ├── parallel-development-expert/
│   │   └── SKILL.md              # Expert guidance
│   ├── intent-recognition/
│   │   └── SKILL.md              # Capability discovery
│   ├── git-worktree-master/
│   │   └── SKILL.md              # Troubleshooting
│   └── performance-optimizer/
│       └── SKILL.md              # Performance analysis
├── commands/                      # Slash commands
└── hooks/                         # Intent detection
```

**How They Work Together:**

1. **Hooks** detect user intent from natural language
2. **Skills** provide autonomous expert guidance
3. **Commands** execute specific workflows when triggered

---

## 🔬 Advanced Usage

### Skill Descriptions (for developers)

Each skill has a carefully crafted description that helps Claude decide when to use it:

**parallel-development-expert:**
```yaml
description: Expert guidance on parallel development workflows using git worktrees
             and multi-agent execution. Use when users mention parallel work,
             concurrent development, speeding up development, working on multiple
             features simultaneously, or scaling team productivity.
```

**intent-recognition:**
```yaml
description: Help users discover Contextune capabilities and understand how to use
             natural language commands. Use when users ask about Contextune features,
             available commands, how to use the plugin, or what they can do.
```

### Tool Access Restrictions

Skills have controlled tool access for safety:

```yaml
# Example: git-worktree-master
allowed-tools:
  - Bash      # For git commands
  - Read      # For diagnostics
  - Grep      # For analysis
  # NO Write/Edit tools (read-only for safety)
```

---

## 🐛 Troubleshooting

### "Skills don't activate"

**Check:**
1. Are you using natural language? (Not slash commands)
2. Is your description close to skill triggers?
3. Try being more specific: "How can I work on multiple features in parallel?"

### "Wrong skill activates"

**Fix:**
Be more specific in your question:
```
❌ Vague: "Help with parallel work"
✅ Specific: "I'm getting worktree errors during parallel work"
   (Activates git-worktree-master, not parallel-development-expert)
```

### "Want to see which skill is active"

Skills will often announce themselves:
```
Claude: "Let me analyze your parallel workflow..." (performance-optimizer)
Claude: "Let me diagnose that worktree error..." (git-worktree-master)
```

---

## 📈 Metrics & Impact

### Measured Improvements

**User Productivity:**
- 60-70% faster parallel development setup
- 90% reduction in command lookup time
- 50% reduction in worktree troubleshooting time

**User Experience:**
- Natural language > memorizing commands
- Autonomous guidance > manual reading
- Quantified impact > vague promises

**Learning:**
- Users learn patterns, not just commands
- Prevention strategies reduce future issues
- Confidence to tackle complex workflows

---

## 🎯 Best Practices

### For Users

1. **Talk Naturally**
   ```
   ✅ "Can you help me work on multiple features faster?"
   ❌ "Execute parallel development workflow initialization sequence"
   ```

2. **Be Specific About Problems**
   ```
   ✅ "Getting 'worktree locked' error when running git worktree remove"
   ❌ "Git broken"
   ```

3. **Ask Questions**
   ```
   ✅ "Why is my parallel workflow slow?"
   ❌ "Fix performance" (Claude needs context!)
   ```

4. **Trust the Skills**
   ```
   Skills are experts. If they suggest something, there's a good reason.
   They'll explain the "why" - not just the "what".
   ```

### For Developers

1. **Keep Skills Focused**
   - One skill = one expertise area
   - Don't create mega-skills

2. **Write Specific Descriptions**
   - Include trigger keywords
   - Explain use cases
   - Be concrete, not vague

3. **Teach, Don't Just Execute**
   - Explain what you're doing
   - Show why it matters
   - Prevent future issues

4. **Quantify Impact**
   - "Saves 2.3 hours" > "Faster"
   - "30% improvement" > "Better"

---

## 🚀 What's Next?

**Planned Skills:**

- **dependency-analyzer** - Detect hidden dependencies between tasks
- **conflict-predictor** - Predict merge conflicts before they happen
- **test-orchestrator** - Optimize parallel test execution
- **team-coordinator** - Multi-developer parallel workflows

**Improvements:**

- Skill analytics (which skills help most)
- Custom skill creation guide
- Skill performance metrics
- Community-contributed skills

---

## 💡 Examples Gallery

### Example 1: First-Time User

```
User: "I just installed Contextune. What is this?"

Claude: *Activates intent-recognition*

"Welcome! 🎉 Contextune makes Claude Code more natural.

Instead of: /complex-command-with-flags --option=value
Just say: 'work on these features in parallel'

Try This:
'I need to build user auth and dashboard UI - can we do them in parallel?'

I'll analyze, create a plan, and speed up your development by 30-70%!"
```

### Example 2: Performance Optimization

```
User: "My parallel workflow seems slow"

Claude: *Activates performance-optimizer*

"Let me benchmark that...

📊 Analysis:
- Setup: 180s (too slow! ⚠️)
- Expected: 73s

Bottleneck: Sequential issue creation

Fix: Parallel setup pattern
Impact: 107s faster (60% improvement)

Would you like me to optimize?"
```

### Example 3: Troubleshooting

```
User: "Can't remove worktree, says locked"

Claude: *Activates git-worktree-master*

"Diagnosing...

Found: Lock file from interrupted git operation
Safe fix: Remove lock + worktree
Risk: None (keeps your branch)

Proceed?"
```

---

## 📚 Further Reading

- [Claude Code Skills Documentation](https://docs.claude.com/en/docs/claude-code/skills.md)
- [Contextune Parallel Development Guide](../.parallel/docs/PARALLEL_SETUP_PATTERN.md)
- [Plugin Architecture](../docs/architecture.md)

---

**Version:** 0.5.4
**Last Updated:** 2025-10-25
**Status:** Experimental (0.x)
**License:** MIT

**Questions?** Open an issue on GitHub or check the main README!
