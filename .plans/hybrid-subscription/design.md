# Hybrid Subscription Strategy - Architecture & Implementation Plan

**Type:** Design
**Status:** Complete
**Estimated Tokens:** 95,000

---

## Executive Summary

**Goal:** Enable Contextune users to dramatically reduce costs ($80-100/month savings) by using API keys for parallel operations while maintaining Claude Code Max 5x subscription for interactive work.

**Core Insight:** Parallel workflows (research, planning, execution) consume messages 3-5x faster than interactive use. By routing parallel ops through API, users get better performance at 1/10th the cost.

**Business Impact:**
- **User savings:** $960-1200/year
- **Better UX:** Faster parallel ops (no rate limits)
- **Wider adoption:** Lower cost barrier for power users
- **Competitive advantage:** Unique value proposition

---

## Architecture

[See full architecture document in research output above - this is a summary]

### Core Components

1. **UsageAnalyzer** - Track parallel operations and message consumption
2. **SavingsCalculator** - Calculate cost projections and ROI
3. **HybridConfigManager** - Secure API key storage and validation
4. **RecommendationEngine** - Smart recommendations when beneficial
5. **Setup Wizard** - Interactive `/ctx:configure-hybrid` command

### Data Flow

```
User Operation
    ↓
UsageAnalyzer (track)
    ↓
RecommendationEngine (analyze)
    ↓
Show recommendation (if eligible)
    ↓
/ctx:configure-hybrid (setup)
    ↓
API key stored in .claude/settings.local.json
    ↓
Parallel operations use API automatically
```

---

## Implementation Approach

### Phased Rollout (6 Phases)

**Phase 1: Analytics Foundation** (25K tokens, 4-6h)
- UsageAnalyzer implementation
- Database schema for tracking
- Hook integration

**Phase 2: Savings Calculator** (15K tokens, 2-4h)
- Cost projection models
- Breakeven analysis
- Recommendation generation

**Phase 3: Configuration Management** (18K tokens, 3-5h)
- Secure API key storage
- Validation and testing
- Gitignore automation

**Phase 4: Setup Wizard** (20K tokens, 4-6h)
- Interactive `/ctx:configure-hybrid`
- Step-by-step guidance
- Validation and testing

**Phase 5: Recommendation Engine** (12K tokens, 2-3h)
- Automatic recommendations
- Frequency limiting
- A/B testing framework

**Phase 6: Documentation** (5K tokens, 1-2h)
- README updates
- Setup guides
- Video tutorials

**Total:** 95K tokens, 10-14h parallel execution

---

## Task Breakdown

### Phase 1 Tasks

1. **task-1-usage-tracker** (12K tokens)
   - Create `lib/usage_analyzer.py`
   - Track operations in database
   - Calculate message consumption

2. **task-2-hook-integration** (5K tokens)
   - Integrate into `user_prompt_submit.py`
   - Add performance monitoring

3. **task-3-usage-report** (8K tokens)
   - Create `/ctx:usage-report` command
   - Display analytics

### Phase 2 Tasks

4. **task-4-savings-calculator** (10K tokens)
   - Create `lib/savings_calculator.py`
   - Implement cost projections

5. **task-5-savings-report** (5K tokens)
   - Create `/ctx:savings-report` command

### Phase 3 Tasks

6. **task-6-config-manager** (12K tokens)
   - Create `lib/hybrid_config_manager.py`
   - Secure API key storage

7. **task-7-api-integration** (6K tokens)
   - Integrate into parallel commands

### Phase 4 Tasks

8. **task-8-setup-wizard** (20K tokens)
   - Create `/ctx:configure-hybrid`
   - 6-step interactive wizard

### Phase 5 Tasks

9. **task-9-recommendation-engine** (10K tokens)
   - Create `lib/recommendation_engine.py`

10. **task-10-recommendation-hook** (2K tokens)
    - Integrate periodic checks

### Phase 6 Tasks

11. **task-11-documentation** (5K tokens)
    - Update all docs

---

## Success Criteria

- [ ] Setup completes in <5 minutes
- [ ] 80%+ of eligible users see recommendation
- [ ] 50%+ acceptance rate
- [ ] Savings within 10% of projections
- [ ] No security vulnerabilities
- [ ] API keys never committed to git
- [ ] Performance overhead <10ms per operation

---

## Key Features

### 1. Automatic Usage Analytics
```python
# Tracks every operation automatically
analyzer = UsageAnalyzer()
stats = analyzer.get_usage_stats(30)
# → Shows: 65 parallel ops, Max 20x tier, $200/month
```

### 2. Smart Savings Calculator
```python
calculator = SavingsCalculator()
report = calculator.calculate_savings("max_20x", 65)
# → Current: $200/month, Hybrid: $114/month
# → Savings: $86/month ($1,032/year)
```

### 3. Secure API Key Storage
```python
config = HybridConfigManager()
config.set_api_key("sk-ant-...")
# → Stored in .claude/settings.local.json
# → File permissions: 600
# → Auto-added to .gitignore
```

### 4. Interactive Setup Wizard
```bash
/ctx:configure-hybrid

# Step 1: Analyze usage → Shows current costs
# Step 2: Calculate savings → Shows potential savings
# Step 3: Get API key → Link + instructions
# Step 4: Configure → Secure storage
# Step 5: Validate → Test API key
# Step 6: Success! → Ready to use
```

### 5. Automatic Recommendations
```
After 30 days of usage...

💡 Save $86/month with Hybrid Mode

Your usage: 65 parallel ops/month
Current: Max 20x ($200/month)
Hybrid: Max 5x + API ($114/month)

Run /ctx:configure-hybrid to start
```

---

## Risk Mitigation

### Technical Risks
- **API pricing changes** → Monitor monthly, update calculator
- **API key security** → 600 permissions, auto-gitignore
- **Tier detection** → Allow manual override
- **Performance** → Async operations, <10ms overhead

### UX Risks
- **Setup complexity** → Step-by-step wizard, video tutorial
- **Recommendation fatigue** → 7-day limit, easy dismiss
- **Savings accuracy** → Conservative estimates, real data tracking

### Business Risks
- **Low adoption** → Clear value prop, success stories
- **Policy changes** → Monitor ToS, maintain fallback

---

## Rollout Plan

**Week 1-2:** Beta testing (10 users)
**Week 3-4:** Limited release (Max 20x users)
**Week 5+:** General availability (all users)

---

## Value Proposition

**"Get Max 20x performance for Max 5x price"**

- Save $80-100/month on Claude subscription
- Unlimited parallel operations via API
- Smart routing (automatic, zero-config)
- 5-minute setup, immediate ROI
- $960-1,200/year savings

---

## Next Steps

1. **Review this design** - Confirm architecture approach
2. **Create task plan** - Break into parallel-executable tasks
3. **Execute with /ctx:execute** - Implement in parallel worktrees
4. **Test with beta users** - Validate savings calculations
5. **Launch** - Roll out to all users

**Estimated implementation:** 10-14 hours parallel, $65-100 cost

---

**Ready to implement!** 🚀
