"""Execution context tracking for quacc workflows."""

from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from enum import Enum
from functools import wraps
from typing import TYPE_CHECKING
from quacc.utils.files import make_unique_dir


if TYPE_CHECKING:
    from collections.abc import Callable


class NodeType(Enum):
    """Type of workflow node."""

    JOB = "job"
    FLOW = "flow"
    SUBFLOW = "subflow"


@dataclass(frozen=True)
class ContextNode:
    """A node in the execution context stack."""

    name: str
    node_type: NodeType


# The execution context stack
_execution_context: ContextVar[tuple[ContextNode, ...]] = ContextVar(
    "_execution_context", default=()
)
_directory_context: ContextVar[str] = ContextVar(
    "_directory_context", default=""
)


def get_context() -> tuple[ContextNode, ...]:
    """Get the full execution context as a tuple of nodes (outermost first)."""
    return _execution_context.get()


def set_context(ctx: tuple[ContextNode, ...]) -> None:
    """Set the execution context directly (used for restoring serialized context)."""
    _execution_context.set(ctx)


def get_directory_context() -> str:
    return _directory_context.get()


def set_directory_context(dir_path: str) -> None:
    """Set the directory context directly (used for restoring serialized context)."""
    _directory_context.set(dir_path)


def is_top_level() -> bool:
    return get_context() is None


def get_context_path() -> str:
    """Get a string representation of the context path (e.g., 'flow1/job1/job2')."""
    return "/".join(n.name for n in get_context())


@contextmanager
def _push_context(name: str, node_type: NodeType):
    """Push a new node onto the execution context stack."""
    old = _execution_context.get()
    new = old + (ContextNode(name, node_type),)
    token = _execution_context.set(new)
    try:
        yield
    finally:
        _execution_context.reset(token)


@contextmanager
def _push_directory_context(directory_path: str):
    token = _directory_context.set(directory_path)
    try:
        yield
    finally:
        _directory_context.reset(token)


def directory_context(directory_path: str):
    return _push_directory_context(directory_path)


def flow_context(name: str):
    """Context manager for flow execution."""
    return _push_context(name, NodeType.FLOW)


def tracked(node_type: NodeType):
    """
    Decorator factory that wraps a function to track its execution context.

    Use this to wrap functions before passing them to workflow engine decorators.

    For workflow engines that serialize tasks and execute them in separate
    processes (like Redun), the context can be passed via special kwargs
    (_quacc_ctx, _quacc_dir) which are extracted and restored before execution.
    """

    def decorator(func: Callable) -> Callable:

        from quacc import get_settings
        settings = get_settings()
        if not settings.AUTODISCOVER_DIR:
            return func

        @wraps(func)
        def wrapper(*args, **kwargs):
            # Check for pre-captured context (from declaration-time engines like Redun)
            precaptured_ctx = kwargs.pop('_quacc_ctx', None)
            precaptured_dir = kwargs.pop('_quacc_dir', None)

            # Restore pre-captured context if provided
            if precaptured_ctx is not None:
                set_context(precaptured_ctx)
            if precaptured_dir is not None:
                set_directory_context(precaptured_dir)

            if is_top_level():
                job_results_dir = settings.RESULTS_DIR.resolve()
                if settings.WORKFLOW_ENGINE == "jobflow" or settings.CREATE_UNIQUE_DIR:
                    job_results_dir = make_unique_dir(
                        base_path=job_results_dir, prefix="quacc-")

                with directory_context(str(job_results_dir)):
                    with _push_context(func.__name__, node_type):
                        return func(*args, **kwargs)
            else:
                with _push_context(func.__name__, node_type):
                    return func(*args, **kwargs)

        return wrapper

    return decorator
