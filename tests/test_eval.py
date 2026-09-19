"""Tests for graders, harness, and reporters."""
import pytest
from agent_eval.models import Task, AgentResult
from agent_eval.graders import KeywordGrader, RegexGrader, ExactGrader, ContainsGrader, grader_for
from agent_eval.harness import EvalHarness
from agent_eval.reporters import to_console, to_markdown
from agent_eval.suites import builtin_suite


def _task(**kw):
    base = dict(id="t1", prompt="p", category="coding")
    base.update(kw)
    return Task(**base)


def _res(out, err=None):
    return AgentResult(task_id="t1", output=out, error=err)


def test_keyword_grader_pass_and_fail():
    t = _task(metadata={"keywords": ["alpha", "beta"]})
    assert KeywordGrader().grade(t, _res("alpha and beta here")).passed
    assert not KeywordGrader().grade(t, _res("alpha only")).passed


def test_regex_grader():
    t = _task(metadata={"pattern": r"\d{3}-\d{4}"})
    assert RegexGrader().grade(t, _res("call 555-1234")).passed
    assert not RegexGrader().grade(t, _res("no digits")).passed


def test_exact_grader_whitespace_insensitive():
    t = _task(reference="a  b", metadata={"grader": "exact"})
    assert grader_for(t).grade(t, _res("a b")).passed
    assert not grader_for(t).grade(t, _res("a c")).passed


def test_contains_grader():
    t = _task(reference="Paris", metadata={"grader": "contains"})
    assert ContainsGrader().grade(t, _res("The answer is Paris.")).passed


def test_error_always_fails():
    t = _task(reference="x", metadata={"grader": "contains"})
    assert not ContainsGrader().grade(t, _res("x", err="boom")).passed


def test_harness_retries_and_survives_exceptions():
    calls = {"n": 0}

    def flaky(task):
        calls["n"] += 1
        if calls["n"] < 2:
            raise RuntimeError("transient")
        return "Paris"

    t = _task(id="cap", reference="Paris", metadata={"grader": "contains"})
    report = EvalHarness(agent=flaky, tasks=[t], max_retries=2).run()
    assert report.scores[0].passed and calls["n"] == 2


def test_report_aggregates():
    tasks = builtin_suite()
    report = EvalHarness(agent=lambda task: "", tasks=tasks).run()
    assert report.pass_rate == 0.0
    assert "coding" in report.by_category()
    md = to_markdown(report)
    assert "Pass rate" in md and "py-reverse" in md
    assert "FAIL" in to_console(report)
