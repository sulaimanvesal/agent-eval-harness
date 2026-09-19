"""Reporters: console table + Markdown report."""
from agent_eval.models import EvalReport

PASS, FAIL = "PASS", "FAIL"


def to_console(report: EvalReport) -> str:
    lines = [f"Eval report {report.run_id}",
             f"pass rate {report.pass_rate:.0%}   mean score {report.mean_score:.2f}   "
             f"cost ${report.total_cost:.4f}",
             "",
             f"{'task':<18}{'cat':<10}{'grade':<6}{'score':<7}details"]
    for s in report.scores:
        lines.append(f"{s.task_id:<18}{s.category:<10}"
                     f"{PASS if s.passed else FAIL:<6}{s.score:<7.2f}{s.details}")
    return "\n".join(lines)


def to_markdown(report: EvalReport) -> str:
    lines = [f"# Eval report `{report.run_id}`", "",
             f"- **Pass rate:** {report.pass_rate:.0%} ({sum(s.passed for s in report.scores)}/{len(report.scores)})",
             f"- **Mean score:** {report.mean_score:.2f}",
             f"- **Total cost:** ${report.total_cost:.4f}", "",
             "## By category"]
    for cat, scores in report.by_category().items():
        rate = sum(s.passed for s in scores) / len(scores)
        lines.append(f"- {cat}: {rate:.0%} ({len(scores)} tasks)")
    lines += ["", "## Tasks", "",
              "| task | category | result | score | details |",
              "|------|----------|--------|-------|---------|"]
    for s in report.scores:
        emoji = "✅" if s.passed else "❌"
        lines.append(f"| {s.task_id} | {s.category} | {emoji} | {s.score:.2f} | {s.details} |")
    return "\n".join(lines) + "\n"
