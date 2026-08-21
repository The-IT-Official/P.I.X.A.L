from human_eval.data import read_problems, HUMAN_EVAL
import json

with open("samples.jsonl") as f:
    attempted = {json.loads(l)["task_id"] for l in f}

problems = read_problems(HUMAN_EVAL)
filtered = {k: v for k, v in problems.items() if k in attempted}

with open("problems_subset.jsonl", "w") as f:
    for p in filtered.values():
        f.write(json.dumps(p) + "\n")

print(f"Wrote {len(filtered)} problems to problems_subset.jsonl")