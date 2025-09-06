"""Integration contract (types) for communicating with the Brain.

This module defines lightweight Pydantic models used by the adapter so the
rest of the system can rely on a stable, validated schema when exchanging
decisions, observations and feedback with the brain. The brain implementation
under `src/intelligence/*` is not modified by this adapter.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field


class Observation(BaseModel):
    kind: str
    payload: dict[str, Any] = Field(default_factory=dict)
    reward: float | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class DecisionContext(BaseModel):
    session_id: str | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    env: dict[str, Any] = Field(default_factory=dict)
    recent_events: list[Observation] = Field(default_factory=list)
    goals: list[str] = Field(default_factory=list)
    constraints: dict[str, Any] = Field(default_factory=dict)


class DecisionResult(BaseModel):
    action_type: str
    action_params: dict[str, Any] = Field(default_factory=dict)
    confidence: float = 0.0
    rationale: str | None = None


class FeedbackBatch(BaseModel):
    observations: list[Observation] = Field(default_factory=list)


class TrainResult(BaseModel):
    status: str
    details: str | None = None
