"""The harness: run agents over tasks, grade, aggregate."""
import time
import uuid
from typing import Callable, List
from agent_eval.models import Task, AgentResult, EvalReport
from agent_eval.graders import grader_for

# AgentFn: takes a Task, returns the raw output string. The harness times it.
AgentFn = Callable[[Task], str]


class LLMBackend:
    """Minimal stub backend. Replace with your real LLM/agent call."""
    def __init__(self, name: str = "stub"):
        self.name = name

    def run(self, task: Task) -> AgentResult:
        return AgentResult(task_id=task.id, output=f"[stub:{self.name}] no output",
                           tool_calls=0, wall_time_s=0.0, cost_usd=0.0)


class EvalHarness:
    def __init__(self, agent: AgentFn, tasks: List[Task],
                 max_retries: int = 1, cost_per_call_usd: float = 0.0):
        self.agent = agent
        self.tasks = tasks
        self.max_retries = max_retries
        self.cost_per_call_usd = cost_per_call_usd

    def _run_once(self, task: Task) -> AgentResult:
        start = time.time()
        try:
            out = self.agent(task)
            err = None
        except Exception as e:                       # noqa: BLE001 - harness must survive agent bugs
            out, err = "", f"{type(e).__name__}: {e}"
        return AgentResult(task_id=task.id, output=out, tool_calls=1,
                           wall_time_s=time.time() - start,
                           cost_usd=self.cost_per_call_usd, error=err)

    def run(self, run_id: str = "") -> EvalReport:
        report = EvalReport(run_id=run_id or f"run-{uuid.uuid4().hex[:8]}")
        for task in self.tasks:
            result = self._run_once(task)
            # retry on error or empty output; keep the last attempt
            for _ in range(self.max_retries - 1):
                if result.error is None and result.output.strip():
                    break
                result = self._run_once(task)
            report.scores.append(grader_for(task).grade(task, result))
        return report
