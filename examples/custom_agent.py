"""Bring your own agent: minimal wiring example."""
from agent_eval.harness import EvalHarness
from agent_eval.reporters import to_console
from agent_eval.suites import builtin_suite


def my_agent(task):
    # Plug in your real agent here, e.g.:
    #   from openai import OpenAI
    #   client = OpenAI()
    #   resp = client.chat.completions.create(model="gpt-4o-mini",
    #       messages=[{"role": "user", "content": task.prompt}])
    #   return resp.choices[0].message.content
    return f"[my_agent] answer to: {task.prompt[:60]}..."


if __name__ == "__main__":
    report = EvalHarness(agent=my_agent, tasks=builtin_suite()).run()
    print(to_console(report))
