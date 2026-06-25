import json
import os
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path


RUNNER_TEMPLATE = """
import importlib.util
import json
import traceback

module_path = "submission.py"
function_name = {function_name!r}
test_case = json.loads({test_case_json!r})

try:
    spec = importlib.util.spec_from_file_location("submission", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    function = getattr(module, function_name)
    actual = function(**test_case["input"])
    print(json.dumps({{"ok": True, "actual": actual}}))
except Exception as exc:
    print(json.dumps({{"ok": False, "error": traceback.format_exc(limit=3)}}))
"""


def extract_function_name(function_signature: str) -> str:
    return function_signature.split("(", 1)[0].strip()


def run_test_cases(code: str, function_signature: str, test_cases: list[dict]) -> tuple[list[dict], str | None]:
    function_name = extract_function_name(function_signature)
    results = []
    first_error = None

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        for index, test_case in enumerate(test_cases):
            case_path = temp_path / f"case_{index}"
            case_path.mkdir()
            submission_path = case_path / "submission.py"
            submission_path.write_text(code, encoding="utf-8")
            _prepare_test_files(case_path, test_case)
            runner_path = case_path / "runner.py"
            runner_path.write_text(
                textwrap.dedent(RUNNER_TEMPLATE).format(
                    function_name=function_name,
                    test_case_json=json.dumps(test_case),
                ),
                encoding="utf-8",
            )

            result = _run_single_test(case_path, runner_path, test_case)
            if result["error"] and not first_error:
                first_error = result["error"]
            results.append(result)

    return results, first_error


def _prepare_test_files(temp_path: Path, test_case: dict) -> None:
    for relative_name, content in test_case.get("files", {}).items():
        file_path = (temp_path / relative_name).resolve()
        if not _is_relative_to(file_path, temp_path.resolve()):
            raise ValueError(f"Invalid test file path: {relative_name}")
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8", newline="")


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def _run_single_test(temp_path: Path, runner_path: Path, test_case: dict) -> dict:
    is_hidden = bool(test_case.get("hidden"))
    base_result = {
        "input": test_case["input"],
        "expected": test_case["expected"],
        "actual": None,
        "passed": False,
        "error": None,
        "file_results": [],
        "hidden": is_hidden,
    }

    try:
        completed = subprocess.run(
            [sys.executable, str(runner_path)],
            cwd=temp_path,
            capture_output=True,
            text=True,
            timeout=3,
            check=False,
            env=_safe_env(),
        )
    except subprocess.TimeoutExpired:
        return _hide_if_needed({**base_result, "error": "Code execution timed out."})

    if completed.returncode != 0:
        return _hide_if_needed({**base_result, "error": completed.stderr.strip() or "Code execution failed."})

    try:
        payload = json.loads(completed.stdout.strip().splitlines()[-1])
    except (json.JSONDecodeError, IndexError):
        return _hide_if_needed({**base_result, "error": "Could not read the program output."})

    if not payload["ok"]:
        return _hide_if_needed({**base_result, "error": payload["error"]})

    actual = payload["actual"]
    file_results = _check_expected_files(temp_path, test_case)
    files_passed = all(result["passed"] for result in file_results)
    result = {
        **base_result,
        "actual": actual,
        "passed": actual == test_case["expected"] and files_passed,
        "file_results": file_results,
    }
    return _hide_if_needed(result)


def _safe_env() -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = ""
    return env


def _check_expected_files(temp_path: Path, test_case: dict) -> list[dict]:
    file_results = []
    for relative_name, expected_content in test_case.get("expected_files", {}).items():
        file_path = (temp_path / relative_name).resolve()
        if not _is_relative_to(file_path, temp_path.resolve()):
            file_results.append(
                {
                    "file": relative_name,
                    "expected": expected_content,
                    "actual": None,
                    "passed": False,
                    "error": "Invalid expected file path.",
                }
            )
            continue

        if not file_path.exists():
            file_results.append(
                {
                    "file": relative_name,
                    "expected": expected_content,
                    "actual": None,
                    "passed": False,
                    "error": "Expected output file was not created.",
                }
            )
            continue

        actual_content = file_path.read_text(encoding="utf-8")
        file_results.append(
            {
                "file": relative_name,
                "expected": expected_content,
                "actual": actual_content,
                "passed": actual_content == expected_content,
                "error": None,
            }
        )
    return file_results


def _hide_if_needed(result: dict) -> dict:
    if not result.get("hidden"):
        return result

    return {
        **result,
        "input": {"case": "Hidden backend edge test"},
        "expected": "Hidden",
        "actual": "Hidden" if result["passed"] else None,
        "error": None if result["passed"] else "Hidden backend edge test failed.",
        "file_results": [],
    }
