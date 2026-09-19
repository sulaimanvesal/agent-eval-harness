"""CLI: python -m agent_eval.cli --suite builtin [--markdown report.md]"""
import argparse
import sys
from agent_eval.harness import EvalHarness
from agent_eval.reporters import to_console, to_markdown
from agent_eval.suites import load_suite


def demo_agent(task):
    """A tiny scripted agent so the CLI works out of the box without an LLM key."""
    canned = {
        "py-reverse": "def reverse_words(s):\n    return ' '.join(s.split()[::-1])",
        "sql-top-n": "SELECT customer_id, SUM(total) AS v FROM orders GROUP BY customer_id ORDER BY v DESC LIMIT 3;",
        "regex-email": r"^[\w.+-]+@[\w-]+\.[\w.]+$",
        "capital-france": "Paris",
        "sum-formula": "n*(n+1)/2",
        "json-schema": '{"name": "Ada", "age": 36}',
    }
    if task.id not in canned:
        raise RuntimeError(f"demo agent has no answer for {task.id}")
    return canned[task.id]


def main(argv=None):
    ap = argparse.ArgumentParser(description="Evaluate an LLM agent on a task suite.")
    ap.add_argument("--suite", default="builtin", help="task suite name")
    ap.add_argument("--markdown", default="", help="write Markdown report to this path")
    ap.add_argument("--retries", type=int, default=1)
    args = ap.parse_args(argv)

    tasks = load_suite(args.suite)
    harness = EvalHarness(agent=demo_agent, tasks=tasks, max_retries=args.retries)
    report = harness.run()

    text = to_console(report)
    print(text)
    if args.markdown:
        with open(args.markdown, "w") as fh:
            fh.write(to_markdown(report))
        print(f"\nMarkdown report written to {args.markdown}")
    return 0 if report.pass_rate == 1.0 else 1


if __name__ == "__main__":
    sys.exit(main())
