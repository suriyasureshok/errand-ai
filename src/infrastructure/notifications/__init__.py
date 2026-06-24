"""Notification infrastructure package for Errand AI.

This package provides implementations for out-of-band communication,
allowing the pipeline to request human input or send status alerts.
"""

from .telegram import TelegramNotifier

__all__ = [
    "TelegramNotifier",
]
