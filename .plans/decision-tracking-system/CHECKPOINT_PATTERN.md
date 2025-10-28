# Checkpoint Pattern for Long Design Sessions

**Type:** Design
**Status:** Implemented
**Estimated Tokens:** 12000

---

## Overview

Enhanced PreCompact hook that implements checkpoint pattern: extract completed plans to .plans/ at compaction boundaries, enabling long sessions with focused context and cumulative documentation.

---

## Architecture

```yaml
architecture:
  checkpoint_pattern:
    concept: "Compact after each major plan to create checkpoints"

    workflow:
      design_auth:
        - "Design authentication system (5K tokens)"
        - "/compact → Extract to .plans/authentication/"
        - "Context cleared, plan preserved"

      design_api:
        - "Design API layer (5K tokens)"
        - "/compact → Extract to .plans/api/"
        - "Context cleared, API + auth plans preserved"

      design_database:
        - "Design database schema (5K tokens)"
        - "/compact → Extract to .plans/database/"
        - "Context cleared, all 3 plans preserved"

    result:
      - "Cumulative documentation: 3 complete plans"
      - "Working context: Fresh for each plan"
      - "Context bloat: Eliminated"

  components:
    enhanced_precompact:
      file: "hooks/context_preserver.py"
      functions:
        extract_completed_plans:
          - "Scans full transcript"
          - "Detects completion markers (≥2)"
          - "Extracts to .plans/[topic]/"

        preserve_in_progress:
          - "Last message if incomplete (<2 markers)"
          - "Saves to scratch_pad.md"

      behavior:
        - "Step 1: Extract completed plans (checkpoints)"
        - "Step 2: Preserve in-progress work (ephemeral)"
        - "Step 3: Allow compaction to proceed"

  data_flow:
    - from: "User types /compact"
      to: "PreCompact hook"
      data: "Transcript path, session ID"

    - from: "PreCompact hook"
      to: "Full transcript"
      data: "Read all conversation entries"

    - from: "Transcript scan"
      to: "Completed plans"
      data: "Entries with ≥2 completion markers"

    - from: "Completed plans"
      to: ".plans/[topic]/"
      data: "Permanent plan files"

    - from: "Last message"
      to: "scratch_pad.md"
      data: "In-progress work (if any)"

    - from: "Compaction"
      to: "Context cleared"
      data: "Old discussion removed, plans preserved"
```

---

## Completion Markers (What Makes a Plan "Complete")

```yaml
markers:
  metadata_markers:
    - "**Type:** Design | Plan | Architecture"
    - "**Status:** Complete | Ready"

  content_markers:
    - "## Success Criteria"
    - "## Task Breakdown"
    - "Ready for: /ctx:plan"
    - "Ready for: /ctx:execute"

  threshold:
    completed_plan: "≥2 markers"
    in_progress: "<2 markers"

  examples:
    completed:
      text: |
        # JWT Authentication

        **Type:** Design
        **Status:** Complete

        ## Architecture
        ...

        ## Task Breakdown
        ...

        ## Success Criteria
        - [ ] Users can login
      markers: 4 (Type, Status, Task Breakdown, Success Criteria)
      result: "Extracted to .plans/jwt-authentication/ ✅"

    in_progress:
      text: |
        Let me design the authentication flow.

        ## Initial Thoughts
        We should use JWT...
      markers: 0
      result: "Saved to scratch_pad.md ✅"
```

---

## User Experience

### Scenario: Designing 3 Subsystems in One Session

```yaml
long_session_workflow:
  step_1_design_auth:
    user: "Design authentication system"
    me: "[Outputs complete design with extraction-optimized format]"
    context: "5,000 tokens"

    user: "/compact"
    precompact_hook:
      - "Detects completed plan (4 markers)"
      - "Extracts to .plans/authentication/design.md"
      - "No scratch_pad.md (plan was complete)"

    post_compact:
      - "Context cleared (5K tokens freed)"
      - "Auth plan: Permanent in .plans/"

  step_2_design_api:
    user: "Design API layer"
    me: "[Outputs complete design]"
    context: "5,000 tokens (fresh)"

    user: "/compact"
    precompact_hook:
      - "Detects completed plan (4 markers)"
      - "Extracts to .plans/api-layer/design.md"

    post_compact:
      - "Context cleared (another 5K freed)"
      - "API plan: Permanent in .plans/"
      - "Auth plan: Still in .plans/ (referenced if needed)"

  step_3_design_database:
    user: "Design database schema"
    me: "[Outputs complete design]"
    context: "5,000 tokens (fresh)"

    user: "/compact"
    precompact_hook:
      - "Detects completed plan"
      - "Extracts to .plans/database/design.md"

    post_compact:
      - "All 3 plans: Permanent in .plans/"
      - "Context: Clean for implementation"

  step_4_implement:
    user: "Implement authentication"
    me: "[Can reference .plans/authentication/design.md]"
    context: "Fresh, focused on implementation"

  total_session:
    plans_created: 3
    context_bloat: "0 (compacted after each)"
    documentation: "3 complete plans in .plans/"
    risk_of_loss: "0 (checkpoints preserved)"
```

---

## Without Checkpoint Pattern (Current Behavior)

```yaml
without_checkpoints:
  same_session:
    design_auth: "5K tokens"
    design_api: "5K tokens"
    design_database: "5K tokens"

    total_context: "15K tokens (all in memory)"

    problems:
      - "Context bloat: 15K tokens"
      - "Can't compact (would lose plans)"
      - "Agent confusion: 3 plans in context"
      - "Focus diluted: Which plan is active?"
      - "Risk: Crash loses all 3 plans"

  session_end:
    sessionend_hook: "Extracts all 3 plans"
    result: "✅ Plans saved"

    but:
      - "Held 15K tokens unnecessarily"
      - "Could have compacted 2 times"
      - "Context pressure on design_database work"
```

---

## With Checkpoint Pattern (New Behavior)

```yaml
with_checkpoints:
  same_session:
    design_auth:
      tokens: "5K"
      compact: "After completion"
      extracted: ".plans/authentication/"
      freed: "5K tokens ✅"

    design_api:
      tokens: "5K (fresh context)"
      compact: "After completion"
      extracted: ".plans/api-layer/"
      freed: "5K tokens ✅"

    design_database:
      tokens: "5K (fresh context)"
      compact: "After completion"
      extracted: ".plans/database/"
      freed: "5K tokens ✅"

  benefits:
    max_context_at_once: "5K (vs 15K)"
    compactions: "3 (vs 0)"
    plans_preserved: "3 (same)"
    risk_of_loss: "Minimal (checkpointed)"
    focus: "Sharp (one plan at a time)"
```

---

## Fidelity: Conversation vs Extracted Files

### Conversation Transcript (Highest Fidelity)

```yaml
conversation_contains:
  full_journey:
    - "User's questions"
    - "My answers"
    - "Alternative approaches discussed"
    - "Rejected options + WHY"
    - "Iterative refinement"
    - "Context of decisions"

  example:
    user: "Why not use MongoDB?"
    me: "MongoDB lacks ACID guarantees we need for transactions..."
    user: "Good point, use PostgreSQL"
    me: "## Decision: PostgreSQL... **Rejected MongoDB because:**..."

  fidelity: "🌟🌟🌟🌟🌟 COMPLETE JOURNEY"
```

### Extracted Files (High Fidelity IF Format Used)

```yaml
extracted_files_contain:
  if_extraction_optimized_format_used:
    structure:
      - "## Context (WHY we need this)"
      - "### Alternatives Considered (What we rejected)"
      - "**Decision:** (What we chose)"
      - "**Rationale:** (WHY we chose it)"
      - "### Consequences (Trade-offs)"

    captures_essential:
      - "✅ WHY (if included in Context section)"
      - "✅ Alternatives (if documented)"
      - "✅ Rationale (if explained)"
      - "❌ User's exact questions"
      - "❌ Discussion flow"

  if_format_not_used:
    structure:
      - "Just the architecture"
      - "Just the tasks"
      - "No WHY, no alternatives"

    fidelity: "🌟🌟 LOW (artifact only)"

  conclusion:
    extraction_optimized_format: "🌟🌟🌟🌟 HIGH (captures essential context)"
    regular_format: "🌟🌟 LOW (loses context)"
```

### Recommendation

```yaml
to_maintain_fidelity:
  requirement: "Use extraction-optimized format with these sections:"

  required_sections:
    - "## Context (WHY we're doing this)"
    - "### Alternatives Considered (Options + reasons for rejection)"
    - "**Decision:** (What + WHY)"
    - "### Consequences (Positive, Negative, Trade-offs)"

  result:
    - "Extracted files capture 80-90% of essential context"
    - "Missing: Exact conversational flow (acceptable loss)"
    - "Preserved: WHY, alternatives, rationale (essential)"
```

---

## Success Criteria

- [ ] PreCompact extracts completed plans to .plans/
- [ ] Completed = ≥2 completion markers
- [ ] Plans saved with title-based slugs
- [ ] Tasks extracted if present
- [ ] In-progress work still saved to scratch_pad.md
- [ ] Enables compact-after-plan workflow
- [ ] Context bloat eliminated
- [ ] Checkpoints prevent work loss

---

## References

- Enhanced Hook: `hooks/context_preserver.py`
- Session End Extractor: `hooks/session_end_extractor.py` (similar logic)
- Extraction Format: `output-styles/extraction-optimized.md`
