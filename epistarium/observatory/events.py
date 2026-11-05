"""Auditable monitoring hooks. Observing a step cannot change its evidence status."""
from contextlib import contextmanager
from contextvars import ContextVar

_step_sink = ContextVar('epistarium_observatory_step_sink', default=None)

@contextmanager
def observe_steps(callback):
    token = _step_sink.set(callback)
    try:
        yield
    finally:
        _step_sink.reset(token)

def emit_step(record):
    sink = _step_sink.get()
    if sink:
        # Observatory is an optional sidecar; a failed monitor must not mutate
        # the scientific result or change the result of Jorhas execution.
        try:
            sink(dict(record))
        except (OSError, RuntimeError, ValueError, TypeError):
            pass
