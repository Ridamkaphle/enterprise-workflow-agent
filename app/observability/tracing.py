"""Distributed tracing utilities."""

from contextlib import contextmanager
from typing import Generator


@contextmanager
def trace_span(name: str) -> Generator[None, None, None]:
    """Context manager for a trace span."""
    yield
