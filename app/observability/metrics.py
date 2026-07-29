"""Application metrics instrumentation."""

from typing import Any


def record_metric(name: str, value: float, tags: dict[str, Any] | None = None) -> None:
    """Record a metric data point."""
    _ = tags
    # Wire to Prometheus / OpenTelemetry in implementation phase.
    pass
