from langchain_core.tools import tool
import subprocess
import os

@tool
def create_file(path: str, content: str) -> str:
    """Creates a file at the given path with the given content."""
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    return f"File created at {path}"

@tool
def read_file(path: str) -> str:
    """Reads and returns the content of a file at the given path."""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

@tool
def edit_file(path: str, old_str: str, new_str: str) -> str:
    """Replaces old_str with new_str in the file at the given path."""
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    if old_str not in content:
        return f"String not found in {path}"
    content = content.replace(old_str, new_str)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    return f"Edited {path} successfully"

@tool
def delete_file(path: str) -> str:
    """Deletes the file at the given path."""
    if not os.path.exists(path):
        return f"File {path} does not exist"
    os.remove(path)
    return f"Deleted {path}"

@tool
def list_directory(path: str) -> list:
    """Lists all files and folders in the given directory path."""
    return os.listdir(path)

@tool
def create_directory(path: str) -> str:
    """Creates a directory at the given path, including any missing parents."""
    os.makedirs(path, exist_ok=True)
    return f"Directory created at {path}"

@tool
def run_terminal(command: str) -> str:
    """Runs a shell command and returns its stdout and stderr output."""
    result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
    return result.stdout + result.stderr

@tool
def run_python_file(filepath: str) -> str:
    """Executes a Python file and returns its stdout and stderr output."""
    result = subprocess.run(["python3", filepath], capture_output=True, text=True, timeout=30)
    return result.stdout + result.stderr

@tool
def install_package(package_name: str) -> str:
    """Installs a Python package using pip3 and returns the output."""
    result = subprocess.run(["pip3", "install", package_name], capture_output=True, text=True)
    return result.stdout + result.stderr

@tool
def check_python_version() -> str:
    """Returns the current Python version."""
    result = subprocess.run(["python3", "--version"], capture_output=True, text=True)
    return result.stdout + result.stderr

@tool
def run_code_in_sandbox(code: str, language: str = "python") -> str:
    """Runs code inside an isolated Docker container and returns the output. Safer than running directly."""
    if language == "python":
        image = "python:3.11-slim"
        command = ["docker", "run", "--rm",
                   "--network", "none", 
                   "--memory", "128m",
                   "--cpus", "0.5",
                   image,
                   "python", "-c", code]

    else:
        return f"Language {language} not supported yet."

    result = subprocess.run(command, capture_output=True, text=True, timeout=15)

    return result.stdout + result.stderr

agent_tools = [create_file, read_file, edit_file, delete_file,
               list_directory, create_directory, run_terminal, run_python_file,
               install_package, check_python_version,
               run_code_in_sandbox]

if __name__ == "__main__":
    print(run_code_in_sandbox.invoke({
        "code": "print('hello from sandbox')",
        "language": "python"
    }))
