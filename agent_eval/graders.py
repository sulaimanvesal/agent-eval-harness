"""Graders: turn (task, agent output) into a scored TaskScore."""
import re
from typing import List
from agent_eval.models import Task, AgentResult, TaskScore


class Grader:
    name = "base"

    def grade(self, task: Task, result: AgentResult) -> TaskScore:
        raise NotImplementedError


class KeywordGrader(Grader):
    """Passes if every keyword listed in task.metadata['keywords'] appears in the output."""
    name = "keyword"

    def grade(self, task: Task, result: AgentResult) -> TaskScore:
        keywords: List[str] = task.metadata.get("keywords", [])
        hay = result.output.lower()
        missing = [k for k in keywords if k.lower() not in hay]
        passed = not missing and result.error is None
        score = 1.0 - len(missing) / max(len(keywords), 1)
        return TaskScore(task.id, task.category, task.difficulty, passed,
                         max(score, 0.0),
                         f"missing keywords: {missing}" if missing else "all keywords present",
                         result.tool_calls, result.wall_time_s, result.cost_usd)


class RegexGrader(Grader):
    """Passes if task.metadata['pattern'] matches the output (multiline regex)."""
    name = "regex"

    def grade(self, task: Task, result: AgentResult) -> TaskScore:
        pattern = task.metadata.get("pattern", "")
        match = re.search(pattern, result.output, re.MULTILINE | re.DOTALL) if pattern else None
        passed = match is not None and result.error is None
        return TaskScore(task.id, task.category, task.difficulty, passed,
                         1.0 if passed else 0.0,
                         f"pattern {'matched' if passed else 'not found'}: {pattern!r}",
                         result.tool_calls, result.wall_time_s, result.cost_usd)


class ExactGrader(Grader):
    """Passes if output stripped equals task.reference stripped (whitespace-normalized)."""
    name = "exact"

    @staticmethod
    def _norm(s: str) -> str:
        return re.sub(r"\s+", " ", s.strip())

    def grade(self, task: Task, result: AgentResult) -> TaskScore:
        ref = self._norm(task.reference or "")
        got = self._norm(result.output)
        passed = ref == got and result.error is None
        return TaskScore(task.id, task.category, task.difficulty, passed,
                         1.0 if passed else 0.0,
                         "exact match" if passed else f"expected {ref!r}, got {got!r}",
                         result.tool_calls, result.wall_time_s, result.cost_usd)


class ContainsGrader(Grader):
    """Passes if task.reference (or metadata['contains']) is a substring of the output."""
    name = "contains"

    def grade(self, task: Task, result: AgentResult) -> TaskScore:
        needle = task.reference or task.metadata.get("contains", "")
        passed = needle in result.output and result.error is None
        return TaskScore(task.id, task.category, task.difficulty, passed,
                         1.0 if passed else 0.0,
                         f"{'found' if passed else 'missing'} substring {needle!r}",
                         result.tool_calls, result.wall_time_s, result.cost_usd)


def grader_for(task: Task) -> Grader:
    kind = task.metadata.get("grader", "contains")
    return {"keyword": KeywordGrader(), "regex": RegexGrader(),
            "exact": ExactGrader(), "contains": ContainsGrader()}[kind]
