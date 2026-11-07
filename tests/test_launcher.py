import json
import subprocess
import sys
from pathlib import Path


def test_launcher_selects_project_from_other_directory(tmp_path):
    result = subprocess.run(
        [sys.executable, str(Path("start_app.py").resolve()), "--help"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "--no-browser" in result.stdout


def test_vscode_launch_and_task():
    launch = json.loads(Path(".vscode/launch.json").read_text())["configurations"][0]
    task = json.loads(Path(".vscode/tasks.json").read_text())["tasks"][0]
    assert launch["program"] == "${workspaceFolder}/start_app.py"
    assert task["args"] == ["${workspaceFolder}/start_app.py"]
    assert task["type"] == "process"
