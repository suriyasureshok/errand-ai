"""Persistence package for the Errand AI pipeline.

This package isolates all raw disk I/O operations from the application's
business logic. It provides atomic state management and append-only
event ledgers to guarantee data integrity across pipeline executions.
"""

from .event_store import EventStore
from .session_store import SessionStore

# Explicitly define the public API of the persistence package.
__all__ = [
    "EventStore",
    "SessionStore",
]
