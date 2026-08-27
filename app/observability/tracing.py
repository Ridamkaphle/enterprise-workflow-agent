"""Distributed tracing utilities."""

from collections.abc import Generator
from contextlib import contextmanager


@contextmanager
def trace_span(name: str) -> Generator[None, None, None]:
    """Context manager for a trace span."""
    yield
