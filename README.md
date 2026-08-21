# P.I.X.A.L

> "I am P.I.X.A.L. — Primary Interactive X-ternal Assistant Life-form or Pix for short. I was built to assist, to reason, and to act."
> Inspired by the AI character from Ninjago, P.I.X.A.L is an autonomous coding agent that doesn't just respond — it thinks, acts, observes, and iterates until the job is done.

---

## What It Is

P.I.X.A.L is a fully autonomous coding agent built on a ReAct loop (Thought → Action → Observation) using LangGraph orchestration and Groq-hosted Llama 3.3-70B. It can plan multi-step solutions, write and execute code, manage files, run shell commands, search the web, and remember context across sessions using ChromaDB vector memory. All untrusted code execution is sandboxed inside Docker containers.

Benchmarked on the HumanEval hard subset (problems 100-163): **73.4% pass@1 (47/64)**

---

## Architecture

```
User Input
    |
    v
[LangGraph StateGraph]
    |
    |---> agent_node (Llama 3.3-70B via Groq)
    |         |
    |         |-- has tool_calls? --> [ToolNode] --> back to agent_node
    |         |
    |         |-- no tool_calls?  --> END (final answer)
    |
    v
Streaming Output
```

The agent state is a simple message list annotated with `operator.add` so every turn appends rather than overwrites. The system prompt injects the ReAct reasoning contract at the top of every invocation.

### Core Files

```
P.I.X.A.L/
├── agent/
│   ├── graph.py        # LangGraph ReAct loop, StateGraph, streaming entrypoint
│   ├── llm.py          # Groq client setup, tool binding, system prompt
│   ├── memory.py       # ChromaDB PersistentClient, remember/recall/forget tools
│   ├── tools.py        # 14 tools: file I/O, shell, Docker sandbox, and more
│   └── main.py         # CLI entrypoint
├── eval/
│   ├── eval.py                       # Generates completions → samples.jsonl
│   ├── clean_samples.py              # Strips markdown fences, fixes indentation
│   ├── prep_eval.py                  # Filters problems to evaluated subset
│   ├── run_eval.py                   # Runs evaluate_functional_correctness
│   ├── samples.jsonl                 # Model completions (64 problems)
│   ├── samples.jsonl_results.jsonl   # Benchmark results (73.4% pass@1)
│   └── problems_subset.jsonl         # HumanEval problems 100-163
├── .dockerignore
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Tool Suite (14 tools)

### File Operations
| Tool | Description |
|---|---|
| `create_file(path, content)` | Creates a file at the given path |
| `read_file(path)` | Reads and returns file content |
| `edit_file(path, old_str, new_str)` | Replaces a string in a file |
| `delete_file(path)` | Deletes a file |
| `list_directory(path)` | Lists all files and folders in a directory |
| `create_directory(path)` | Creates a directory including missing parents |

### Execution
| Tool | Description |
|---|---|
| `run_terminal(command)` | Runs a shell command, returns stdout + stderr |
| `run_python_file(filepath)` | Executes a Python file, returns output |
| `run_code_in_sandbox(code, language)` | Runs code in isolated Docker container (python:3.11-slim, no network, 128MB RAM, 0.5 CPU) |

### Package Management
| Tool | Description |
|---|---|
| `install_package(package_name)` | Installs a Python package via pip3 |
| `check_python_version()` | Returns current Python version |

### Memory (ChromaDB)
| Tool | Description |
|---|---|
| `remember(text, metadata)` | Stores a memory with metadata (type, status, etc.) |
| `recall(query, n_results)` | Semantic search over past memories |
| `forget(memory_id)` | Deletes a memory by ID |

Memory persists across sessions via `chromadb.PersistentClient` stored locally at `./neuroforge_memory`.

---

## Benchmark Results

Evaluated on HumanEval hard subset (problems 100-163, 64 total) using Llama 3.3-70B via Groq API.

| Metric | Result |
|---|---|
| Subset | HumanEval/100 - HumanEval/163 |
| Problems attempted | 64 |
| pass@1 | **73.4% (47/64)** |
| Model | llama-3.3-70b-versatile |
| Temperature | 0.0 |
| Timeout per problem | 10s |

Full results in `eval/samples.jsonl_results.jsonl`.

### Eval Pipeline

The benchmark was not a single script. It was a multi-stage pipeline built and debugged from scratch:

1. `eval.py` -- calls Groq API for each of the 64 problems, streams completions to `samples.jsonl` with resume support (skips already-completed problems on restart)
2. `clean_samples.py` -- strips markdown code fences and fixes first-line indentation bugs that caused early runs to score 0.0
3. `prep_eval.py` -- filters the full HumanEval problem set down to the evaluated subset, writes `problems_subset.jsonl`
4. `run_eval.py` -- runs `evaluate_functional_correctness` with `n_workers=1` and `timeout=10s`

Early runs scored 0.0 and 1.5% due to the model returning completions with missing 4-space indentation on the first line. `clean_samples.py` was written to catch and fix this before eval, which brought the score to 73.4%.

---

## Setup

### Prerequisites

- Python 3.11+
- Docker (required for sandboxed code execution)
- A Groq API key (free at console.groq.com)

### Installation

```bash
git clone https://github.com/The-IT-Official/P.I.X.A.L.git
cd P.I.X.A.L

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### Environment

```bash
cp .env.example .env
# Open .env and add your Groq API key
```

`.env`:
```
GROQ_API_KEY=your_groq_api_key_here
```

### Run the Agent

```bash
python agent/main.py
```

You will see a `User:` prompt. Type any coding task and P.I.X.A.L will reason through it, call tools, and stream its output step by step.

Example:
```
User: Create a Python script that reads a CSV file and prints the average of the third column
[agent]
I'll create a Python script to read a CSV and compute the column average.
[tools]
  → create_file({'path': 'avg.py', 'content': '...'})
[agent]
Script created. Running it to verify...
[tools]
  → run_python_file({'filepath': 'avg.py'})
[agent]
Output confirmed. File is at avg.py.
```

### Reproduce the Benchmark

Install human-eval separately (not in requirements.txt -- dev only):
```bash
pip install git+https://github.com/openai/human-eval.git
```

Then run the pipeline in order:
```bash
python eval/eval.py           # generates samples.jsonl (~64 Groq API calls)
python eval/clean_samples.py  # fixes formatting
python eval/prep_eval.py      # builds problems_subset.jsonl
python eval/run_eval.py       # prints final pass@1 score
```

Note: `eval.py` has resume support -- if it gets interrupted by a rate limit it will pick up where it left off on the next run.

---

## Stack

| Component | Technology |
|---|---|
| Orchestration | LangGraph |
| LLM | Llama 3.3-70B via Groq |
| Vector Memory | ChromaDB (PersistentClient) |
| Code Sandbox | Docker (python:3.11-slim) |
| Language | Python 3.11 |

---

## What's Next

- FastAPI wrapper for HTTP access
- Streamlit demo frontend
- Web search tool integration
