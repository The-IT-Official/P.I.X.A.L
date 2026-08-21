from multiprocessing import freeze_support

if __name__ == "__main__":
    freeze_support()
    from human_eval.evaluation import evaluate_functional_correctness
    results = evaluate_functional_correctness(
        "samples.jsonl",
        k=[1],
        n_workers=1,
        timeout=10.0,
        problem_file="problems_subset.jsonl"
    )
    print(results)