You're absolutely right - we need to integrate features.yaml AND leverage Claude Code's conversation history. Let me redesign:

  What We Have

  1. history.jsonl (1,236 conversations!)
  {"display": "prompt", "timestamp": ..., "project": "..."}

  2. observability_db.py (already tracking)
  - Sessions, detections, performance, errors
  - Has session IDs we can link to!

  3. features.yaml (tracking 15 features)
  - Should be integrated with decision system

  ---
  Redesigned Architecture: Unified Context System

  decisions.yaml Structure (Enhanced)

  metadata:
    project: "contextune"
    auto_population_enabled: true  # NEW!
    last_conversation_scan: "2025-10-27T20:00:00Z"
    conversation_source: "~/.claude/history.jsonl"

  # NEW: Link to conversation history
  conversations:
    scanned_count: 1236
    last_scanned_timestamp: 1729771380131
    sessions_with_decisions: 15

  # Existing sections with conversation links
  research:
    - id: "res-001"
      # ... existing fields ...

      # NEW: Link to conversation
      conversation_link:
        session_id: "abc123"
        timestamp: 1729771380131
        prompt: "Research token estimation methodologies"
        history_line: 1234

  # NEW: Features section (integrate features.yaml)
  features:
    - id: "feat-001"
      title: "Haiku 4.5 Integration"
      # Copy from features.yaml
      estimated_tokens: 10000
      status: "planned"

      # NEW: Link to decision
      based_on_decision: ["dec-001"]

      # NEW: Link to conversation
      conversation_link:
        session_id: "def456"
        discussed_at: 1729770000000

  decisions:
    - id: "dec-001"
      # ... existing fields ...

      # NEW: Link to conversation
      conversation_link:
        session_id: "abc123"
        timestamp: 1729771380131

      # NEW: Link to observability DB
      observability_link:
        detection_id: 123
        session_metrics: "observability.db#sessions"

  ---
  Auto-Population Pipeline

  Script: decision-sync.py

  #!/usr/bin/env -S uv run --script
  # /// script
  # requires-python = ">=3.10"
  # dependencies = ["pyyaml>=6.0", "rich>=13.0.0"]
  # ///
  """
  Auto-populate decisions.yaml from:
  1. Claude Code conversation history (~/.claude/history.jsonl)
  2. Contextune observability DB (lib/observability_db.py)
  3. Features.yaml (integrate feature tracking)
  """

  def scan_conversations():
      """Parse history.jsonl for decision keywords."""
      with open("~/.claude/history.jsonl") as f:
          for line in f:
              entry = json.loads(line)
              prompt = entry["display"]

              # Detect research
              if any(kw in prompt.lower() for kw in [
                  "research", "/ctx:research", "investigate", "explore"
              ]):
                  extract_research(entry)

              # Detect planning
              if any(kw in prompt.lower() for kw in [
                  "/ctx:plan", "create plan", "break down", "design"
              ]):
                  extract_plan(entry)

              # Detect decisions
              if any(kw in prompt.lower() for kw in [
                  "why did we choose", "decision", "we decided",
                  "architecture decision", "should we use"
              ]):
                  extract_decision(entry)

  def link_to_observability():
      """Link decisions to observability DB sessions."""
      # Query observability_db.py for session data
      # Cross-reference timestamps
      # Add detection/performance links

  def integrate_features():
      """Sync features.yaml into decisions.yaml."""
      # Read features.yaml
      # Create feature entries in decisions.yaml
      # Link features to decisions they implement

  ---
  Updated Plan Structure

  .plans/decision-tracking-system/
  ├── plan.yaml
  ├── tasks/
  │   ├── task-1.md  (decisions.yaml schema) ✅
  │   ├── task-2.md  (decision-search.py)
  │   ├── task-3.md  (decision-add.py)
  │   ├── task-4.md  (decision-lifecycle.py)
  │   ├── task-5.md  (decision-sync.py) ⭐ NEW - Auto-populate
  │   ├── task-6.md  (decision-link.py) ⭐ NEW - Link conversations
  │   ├── task-7.md  (Skill with auto-detect)
  │   ├── task-8.md  (Hook with sync)
  │   ├── task-9.md  (CLAUDE.md integration)
  │   └── task-10.md (Validation)

  ---
  Key Benefits of Enhanced Design

  ✅ Auto-Population (vs manual tracking)
  - Scan history.jsonl for research/plans/decisions
  - Extract from past 1,236 conversations
  - No manual entry needed

  ✅ Feature Integration (unified system)
  - features.yaml → decisions.yaml#features
  - Link features to decisions they implement
  - Single source of truth

  ✅ Conversation Linking (full context)
  - Click link → see full conversation
  - Session ID → observability DB
  - Timestamp → history.jsonl line

  ✅ Backward Compatible
  - Scans existing conversations (1,236 entries!)
  - Imports existing features.yaml (15 features)
  - Populates decisions.yaml automatically

  ---
  Should I Redesign the Plan?

  Option 1: Update existing plan with 2 new tasks
  - task-5: decision-sync.py (auto-populate from conversations)
  - task-6: decision-link.py (link to observability DB)
  - task-7-10: Renumber existing tasks

  Option 2: Create separate "Phase 2" plan
  - Phase 1: Manual system (what we have)
  - Phase 2: Auto-population (new tasks)

  My recommendation: Option 1 - Build it right the first time with auto-population. This is a game-changer for usability.

  Want me to update the plan with auto-population + feature integration?