from dataclasses import dataclass


@dataclass
class TestResult:
    passed: bool
    stdout: str
    stderr: str
    exit_code: int
    log_file_path: str
