"""Pydantic models for Agent 2 structured output."""

from typing import Literal, Optional
from pydantic import BaseModel, Field


class UXTaskResult(BaseModel):
    """Result of a single UX task evaluation."""
    
    ux_task_nr: int = Field(
        description="The UX task number that was evaluated"
    )
    requirement: str = Field(
        description="The requirement that was tested"
    )
    passed: bool = Field(
        description="Whether the task passed (True) or failed (False)"
    )
    observations: str = Field(
        description="Technical and UX observations during the test (e.g., console errors, double waits, element issues)"
    )
    advice: str = Field(
        default="N/A",
        description="Advice on how to improve the UX (only if 'advice' was true AND 'passed' was false), otherwise 'N/A'"
    )


class UXTestResults(BaseModel):
    """Complete results from all UX task evaluations."""
    
    task_results: list[UXTaskResult] = Field(
        description="List of results for each UX task that was evaluated (excluding the access task)"
    )
    summary: str = Field(
        description="Brief summary of the overall test execution"
    )
