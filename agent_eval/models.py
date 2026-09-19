"""Core data models: Task, AgentResult, EvalReport."""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Task:
    """One evaluation task given to the agent."""
    id: str
    prompt: str
    category: str = "general"
    difficulty: str = "medium"
    reference: Optional[str] = None          # expected answer / patch for grading
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResult:
    """What the agent produced for one task."""
    task_id: str
    output: str
    tool_calls: int = 0
    wall_time_s: float = 0.0
    cost_usd: float = 0.0
    error: Optional[str] = None


@dataclass
class TaskScore:
    task_id: str
    category: str
    difficulty: str
    passed: bool
    score: float                              # 0..1
    details: str
    tool_calls: int
    wall_time_s: float
    cost_usd: float


@dataclass
class EvalReport:
    run_id: str
    scores: List[TaskScore] = field(default_factory=list)

    @property
    def pass_rate(self) -> float:
        return sum(s.passed for s in self.scores) / max(len(self.scores), 1)

    @property
    def mean_score(self) -> float:
        return sum(s.score for s in self.scores) / max(len(self.scores), 1)

    @property
    def total_cost(self) -> float:
        return sum(s.cost_usd for s in self.scores)

    def by_category(self) -> Dict[str, List[TaskScore]]:
        out: Dict[str, List[TaskScore]] = {}
        for s in self.scores:
            out.setdefault(s.category, []).append(s)
        return out
