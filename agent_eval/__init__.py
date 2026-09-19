"""agent-eval: a tiny evaluation harness for LLM coding agents."""
from agent_eval.models import Task, AgentResult, EvalReport
from agent_eval.harness import EvalHarness, LLMBackend

__all__ = ["Task", "AgentResult", "EvalReport", "EvalHarness", "LLMBackend"]
__version__ = "0.1.0"
