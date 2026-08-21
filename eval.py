import json
import os
import time
from dotenv import load_dotenv
from groq import Groq
from human_eval.data import read_problems, HUMAN_EVAL

load_dotenv()
client = Groq()
problems = read_problems(HUMAN_EVAL)

target_ids = {f"HumanEval/{i}" for i in range(100, 164)}
subset = {k: v for k, v in problems.items() if k in target_ids}

# Check which ones already completed so we don't re-run them
completed = set()
try:
    with open("samples.jsonl") as f:
        for line in f:
            completed.add(json.loads(line)["task_id"])
    print(f"Resuming — {len(completed)} already done, {len(subset) - len(completed)} remaining")
except FileNotFoundError:
    print("Starting fresh")

def get_completion(prompt: str) -> str:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
    "role": "system",
    "content": """You are an expert Python programmer. You will be given a Python function signature and docstring. Your job is to write ONLY the function body.

Rules:
- Use exactly 4 spaces for indentation
- Do NOT include the def line or docstring
- Do NOT include markdown, backticks, or any explanation
- Your output gets directly appended after the docstring, so it must be valid Python immediately
- Return ONLY the indented code body, nothing else"""
},
{
    "role": "user",
    "content": f"Complete this function:\n\n{prompt}"
}
        ],
        max_tokens=256,  # reduced from 512 — completions don't need that much
        temperature=0.0
    )
    return response.choices[0].message.content

with open("samples.jsonl", "a") as f:  # append mode — resumes where it left off
    for task_id, problem in subset.items():
        if task_id in completed:
            continue
        print(f"Running {task_id}...")
        try:
            completion = get_completion(problem["prompt"])
            f.write(json.dumps({
                "task_id": task_id,
                "completion": completion
            }) + "\n")
            f.flush()
        except Exception as e:
            print(f"ERROR on {task_id}: {e}")
            print("Waiting 60s for rate limit...")
            time.sleep(60)

print("Done.")