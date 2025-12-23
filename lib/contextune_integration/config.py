#!/usr/bin/env python3
"""Unified configuration schema for Contextune-HtmlGraph integration."""

from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class IntentDetectionConfig(BaseModel):
    """Intent detection thresholds and settings."""

    keyword_threshold: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Minimum confidence for keyword matching (1.0 = exact match)"
    )
    model2vec_threshold: float = Field(
        default=0.85,
        ge=0.0,
        le=1.0,
        description="Minimum confidence for Model2Vec matching"
    )
    semantic_threshold: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Minimum confidence for Semantic Router matching"
    )
    enable_haiku_analysis: bool = Field(
        default=True,
        description="Enable Haiku-powered interactive analysis"
    )


class ParallelExecutionConfig(BaseModel):
    """Parallel execution settings."""

    max_agents: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Maximum number of parallel agents"
    )
    default_model: str = Field(
        default="haiku",
        description="Default model for execution agents"
    )
    timeout_minutes: int = Field(
        default=30,
        ge=1,
        le=120,
        description="Execution timeout in minutes"
    )


class ContextuneConfig(BaseModel):
    """Contextune-specific configuration."""

    intent_detection: IntentDetectionConfig = Field(
        default_factory=IntentDetectionConfig
    )
    parallel_execution: ParallelExecutionConfig = Field(
        default_factory=ParallelExecutionConfig
    )
    data_dir: Path = Field(
        default=Path.home() / ".claude" / "plugins" / "contextune" / "data",
        description="Contextune data directory"
    )


class TrackingConfig(BaseModel):
    """HtmlGraph tracking settings."""

    auto_create_tracks: bool = Field(
        default=True,
        description="Automatically create tracks from /ctx:plan"
    )
    auto_link_features: bool = Field(
        default=True,
        description="Automatically link features to tracks"
    )
    auto_start_features: bool = Field(
        default=True,
        description="Automatically start features on execution"
    )
    track_all_sessions: bool = Field(
        default=True,
        description="Track all Claude Code sessions"
    )


class DashboardConfig(BaseModel):
    """HtmlGraph dashboard settings."""

    port: int = Field(
        default=8080,
        ge=1024,
        le=65535,
        description="Dashboard server port"
    )
    host: str = Field(
        default="localhost",
        description="Dashboard server host"
    )
    show_contextune_metrics: bool = Field(
        default=True,
        description="Show Contextune metrics in dashboard"
    )
    auto_reload: bool = Field(
        default=True,
        description="Auto-reload on file changes"
    )


class HtmlGraphConfig(BaseModel):
    """HtmlGraph-specific configuration."""

    tracking: TrackingConfig = Field(default_factory=TrackingConfig)
    dashboard: DashboardConfig = Field(default_factory=DashboardConfig)
    data_dir: Path = Field(
        default=Path(".htmlgraph"),
        description="HtmlGraph data directory"
    )


class IntegrationConfig(BaseModel):
    """Integration-specific settings."""

    enabled: bool = Field(
        default=True,
        description="Enable Contextune-HtmlGraph integration"
    )
    shared_data_dir: Path = Field(
        default=Path.home() / ".contextune-htmlgraph",
        description="Shared data directory"
    )
    log_level: str = Field(
        default="INFO",
        description="Integration logging level"
    )
    sync_interval_seconds: int = Field(
        default=60,
        ge=10,
        le=3600,
        description="Sync interval in seconds"
    )

    @field_validator('log_level')
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}")
        return v_upper


class UnifiedConfig(BaseModel):
    """Unified configuration for Contextune and HtmlGraph."""

    contextune: ContextuneConfig = Field(default_factory=ContextuneConfig)
    htmlgraph: HtmlGraphConfig = Field(default_factory=HtmlGraphConfig)
    integration: IntegrationConfig = Field(default_factory=IntegrationConfig)

    @classmethod
    def get_default_path(cls) -> Path:
        """Get default config file path."""
        return Path.home() / ".contextune-config.yaml"

    class Config:
        json_schema_extra = {
            "example": {
                "contextune": {
                    "intent_detection": {
                        "keyword_threshold": 1.0,
                        "model2vec_threshold": 0.85,
                        "semantic_threshold": 0.7,
                        "enable_haiku_analysis": True
                    },
                    "parallel_execution": {
                        "max_agents": 5,
                        "default_model": "haiku",
                        "timeout_minutes": 30
                    }
                },
                "htmlgraph": {
                    "tracking": {
                        "auto_create_tracks": True,
                        "auto_link_features": True,
                        "auto_start_features": True
                    },
                    "dashboard": {
                        "port": 8080,
                        "show_contextune_metrics": True
                    }
                },
                "integration": {
                    "enabled": True,
                    "log_level": "INFO"
                }
            }
        }
