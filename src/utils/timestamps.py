"""Utility module for standardized timestamp generation and parsing.

This module ensures that all datetimes generated across the Errand AI pipeline
are strictly UTC and formatted consistently to prevent JSON serialization
errors and ensure timezone-agnostic logging.
"""

from datetime import datetime, timezone


def get_current_utc_iso() -> str:
    """Generates the current UTC time as an ISO 8601 formatted string.

    This format is guaranteed to be JSON serializable and is the standard
    for event payloads, session state tracking, and API communication.

    Returns:
        str: The current UTC datetime formatted as 'YYYY-MM-DDTHH:MM:SSZ'.
    """
    now = datetime.now(timezone.utc)
    # Using replace(microsecond=0) keeps the string clean.
    # Appending 'Z' denotes Zulu time (UTC) natively.
    return now.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def get_filesystem_safe_timestamp() -> str:
    """Generates a filesystem-safe string representation of the current time.

    Useful for naming temporary directories, backup files, or log archives
    without introducing invalid characters like colons or spaces.

    Returns:
        str: The current UTC datetime formatted as 'YYYYMMDD_HHMMSS'.
    """
    now = datetime.now(timezone.utc)
    return now.strftime("%Y%m%d_%H%M%S")


def parse_iso_utc(timestamp_str: str) -> datetime:
    """Parses an ISO 8601 formatted string back into a UTC datetime object.

    Args:
        timestamp_str (str): The ISO 8601 string to parse (e.g., 'YYYY-MM-DDTHH:MM:SSZ').

    Returns:
        datetime: A timezone-aware datetime object set to UTC.

    Raises:
        ValueError: If the provided string is not a valid ISO 8601 format.
    """
    if timestamp_str.endswith("Z"):
        timestamp_str = timestamp_str[:-1] + "+00:00"
    return datetime.fromisoformat(timestamp_str)
