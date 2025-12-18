"""Pydantic models for Agent 3 structured output."""

from enum import Enum
from typing import Optional, Union
from pydantic import BaseModel, Field


class TestType(str, Enum):
    """Types of tests that can be identified."""
    VALIDATION = "validation"
    FUNCTIONAL = "functional"
    INTEGRATION = "integration"
    WORKFLOW = "workflow"
    SETUP = "setup"
    NAVIGATION = "navigation"


class TestDetail(BaseModel):
    """Details of an atomic test step within a grouped test."""

    task_number: Union[int, list[int]] = Field(
        description="The task number(s) from Agent 2 results"
    )
    passed: bool = Field(
        description="Whether this step passed"
    )
    observation: str = Field(
        description="Observation from Agent 2 for this step"
    )
    advice: Optional[str] = Field(
        default=None,
        description="Advice from Agent 2 if step failed"
    )


class GroupedTest(BaseModel):
    """A logical grouping of related atomic test tasks."""

    test_name: str = Field(
        description="Descriptive name of the test scenario"
    )
    description: str = Field(
        description="Detailed explanation of what this test scenario validates and why it matters"
    )
    passed: bool = Field(
        description="Overall pass/fail status (true only if all atomic tasks passed)"
    )
    summary: str = Field(
        description="High-level summary of the test group outcome"
    )
    details: dict[str, TestDetail] = Field(
        description="Breakdown of test steps with descriptive keys"
    )


class TestResults(BaseModel):
    """Complete grouped test results from Agent 3."""

    success: bool = Field(
        description="Overall success (true only if all grouped tests passed)"
    )
    duration_seconds: float = Field(
        description="Total execution time from Agent 2"
    )
    grouped_tests: list[GroupedTest] = Field(
        description="List of logically grouped test scenarios"
    )
    original_atomic_tasks: int = Field(
        description="Total number of atomic tasks from Agent 1"
    )
    grouped_tests_count: int = Field(
        description="Number of grouped tests created"
    )
    excluded_non_test_tasks: list[int] = Field(
        default_factory=list,
        description="Task numbers that were excluded (navigation, tab management only)"
    )
