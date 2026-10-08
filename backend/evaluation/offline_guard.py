"""Block network access while allowing Windows' internal asyncio socketpair."""
import asyncio
import inspect
import socket
from contextlib import ExitStack, contextmanager
from unittest.mock import patch

_ORIGINAL_CONNECT = socket.socket.connect

@contextmanager
def no_network():
    original_connect = _ORIGINAL_CONNECT
    fallback = getattr(socket, "_fallback_socketpair", None)
    def guarded_connect(sock, address):
        caller = inspect.currentframe().f_back
        # Windows emulates socketpair using a loopback TCP pair. Only Python's
        # exact stdlib function may make that internal connection; Ollama cannot.
        if fallback and caller.f_code is fallback.__code__:
            return original_connect(sock, address)
        raise AssertionError("Outbound network blocked during offline tests")
    with ExitStack() as stack:
        stack.enter_context(patch.object(socket.socket,"connect",guarded_connect))
        stack.enter_context(patch.object(socket.socket,"connect_ex",side_effect=AssertionError("Network blocked")))
        stack.enter_context(patch.object(socket,"create_connection",side_effect=AssertionError("Network blocked")))
        stack.enter_context(patch.object(socket,"getaddrinfo",side_effect=AssertionError("Network blocked")))
        stack.enter_context(patch.object(asyncio.BaseEventLoop,"create_connection",side_effect=AssertionError("Network blocked")))
        yield
