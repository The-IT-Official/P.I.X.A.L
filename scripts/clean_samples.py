import json

cleaned = []
with open("samples.jsonl") as f:
    for line in f:
        obj = json.loads(line)
        code = obj["completion"]
        
        # Strip markdown fences
        if "```python" in code:
            code = code.split("```python")[1].split("```")[0]
        elif "```" in code:
            code = code.split("```")[1].split("```")[0]
        
        code = code.strip("\n")  # remove leading/trailing newlines only
        
        # Fix first line missing indentation
        lines = code.split("\n")
        fixed_lines = []
        for l in lines:
            if l and not l.startswith("    ") and not l.startswith("\t"):
                fixed_lines.append("    " + l)
            else:
                fixed_lines.append(l)
        code = "\n".join(fixed_lines)
        
        obj["completion"] = "\n" + code + "\n"
        cleaned.append(obj)

with open("samples.jsonl", "w") as f:
    for obj in cleaned:
        f.write(json.dumps(obj) + "\n")

print(f"Cleaned {len(cleaned)} samples.")