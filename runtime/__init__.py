from .errors import RuntimeErrorReason
from .state import Action, NodeState, NodeStatus
from .transitions import transition

__all__ = [
    "Action",
    "NodeState",
    "NodeStatus",
    "RuntimeErrorReason",
    "RuntimeNode",
    "transition",
]


def __getattr__(name: str):
    if name == "RuntimeNode":
        from .node import RuntimeNode

        return RuntimeNode
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
