"""Built-in task suites."""
from agent_eval.models import Task


def builtin_suite() -> list[Task]:
    return [
        Task(
            id="py-reverse",
            category="coding",
            difficulty="easy",
            prompt="Write a Python function `reverse_words(s)` that reverses the order of words in a string.",
            metadata={"grader": "keyword",
                      "keywords": ["def reverse_words", "split", "join"]},
        ),
        Task(
            id="sql-top-n",
            category="coding",
            difficulty="medium",
            prompt="Write a SQL query returning the top 3 customers by total order value from an `orders(customer_id, total)` table.",
            metadata={"grader": "keyword",
                      "keywords": ["select", "group by", "order by", "limit 3"]},
        ),
        Task(
            id="regex-email",
            category="coding",
            difficulty="medium",
            prompt="Give a regex that matches a simple email address like name@example.com.",
            metadata={"grader": "regex", "pattern": r"[@].*[.]"},
        ),
        Task(
            id="capital-france",
            category="qa",
            difficulty="easy",
            prompt="What is the capital of France?",
            reference="Paris",
            metadata={"grader": "contains"},
        ),
        Task(
            id="sum-formula",
            category="reasoning",
            difficulty="medium",
            prompt="What is the closed-form sum of the first n positive integers? Reply with the formula only.",
            reference="n*(n+1)/2",
            metadata={"grader": "exact"},
        ),
        Task(
            id="json-schema",
            category="coding",
            difficulty="hard",
            prompt="Return a JSON object with exactly the keys 'name' (string) and 'age' (integer) for Ada, 36.",
            metadata={"grader": "regex",
                      "pattern": r'"name"\s*:\s*"Ada".*"age"\s*:\s*36|"age"\s*:\s*36.*"name"\s*:\s*"Ada"'},
        ),
    ]


def load_suite(name: str) -> list[Task]:
    suites = {"builtin": builtin_suite}
    if name not in suites:
        raise ValueError(f"unknown suite {name!r}; available: {sorted(suites)}")
    return suites[name]()
