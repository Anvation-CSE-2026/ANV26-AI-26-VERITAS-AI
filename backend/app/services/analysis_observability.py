"""Optional observer hooks. No logs, content storage or behavior changes by default."""
from contextlib import contextmanager
from contextvars import ContextVar
from functools import wraps
from time import perf_counter

_observer = ContextVar("synthetic_benchmark_observer", default=None)

def emit(event: str, **data) -> None:
    observer = _observer.get()
    if observer is None:
        return
    try:
        observer.event(event, **data)
    except Exception:
        # Telemetry errors must not change model/verification decisions.
        observer.observation_failed = True

@contextmanager
def observation_scope(observer):
    token = _observer.set(observer)
    try:
        yield observer
    finally:
        _observer.reset(token)

@contextmanager
def stage(name: str):
    observer = _observer.get()
    if observer is None:
        yield
        return
    started = perf_counter()
    try:
        span = observer.begin_stage(name, started)
    except Exception:
        observer.observation_failed = True
        yield
        return
    outcome = "completed"
    try:
        yield
    except BaseException:
        outcome = "failed_or_interrupted"
        raise
    finally:
        emit("stage_finished", span_id=span, stage=name, seconds=max(0.0, perf_counter()-started), status=outcome)

def timed(name: str):
    def decorate(function):
        @wraps(function)
        def wrapped(*args, **kwargs):
            with stage(name):
                return function(*args, **kwargs)
        return wrapped
    return decorate
