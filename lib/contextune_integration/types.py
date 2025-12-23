#!/usr/bin/env python3
"""Shared type definitions for Contextune-HtmlGraph integration."""

from enum import Enum
from typing import Literal


# Execution modes
ExecutionMode = Literal["parallel", "sequential", "hybrid"]

# Detection methods
DetectionMethod = Literal["keyword", "model2vec", "semantic_router"]

# Work types
WorkType = Literal[
    "feature-implementation",
    "spike-investigation",
    "bug-fix",
    "maintenance",
    "documentation",
    "planning",
    "review",
    "admin"
]

# Task statuses
TaskStatus = Literal["pending", "in-progress", "done", "blocked"]

# Priority levels
Priority = Literal["blocker", "high", "medium", "low"]


class TrackingEvent(str, Enum):
    """Events that trigger tracking actions."""
    PLAN_CREATED = "plan_created"
    EXECUTION_STARTED = "execution_started"
    TASK_COMPLETED = "task_completed"
    SESSION_ENDED = "session_ended"


class IntegrationStatus(str, Enum):
    """Status of integration components."""
    ENABLED = "enabled"
    DISABLED = "disabled"
    ERROR = "error"
    UNAVAILABLE = "unavailable"
