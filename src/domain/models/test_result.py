"""Domain models for test suite execution outputs.

This module defines the strict structure representing the output of the
target codebase's testing framework.
"""

from dataclasses import dataclass


@dataclass
class TestResult:
    """Encapsulates the raw output of a test execution run.

    Attributes:
        passed (bool): True if the test suite exited cleanly, False otherwise.
        stdout (str): The standard output stream from the test runner.
        stderr (str): The standard error stream from the test runner.
        exit_code (int): The exact OS exit code returned by the subprocess.
        log_file_path (str): The persistent file path where these logs were saved.
    """

    passed: bool
    stdout: str
    stderr: str
    exit_code: int
    log_file_path: str
