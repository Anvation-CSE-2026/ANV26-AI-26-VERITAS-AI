"""Run all backend tests with live opt-ins disabled and outbound sockets blocked."""
import json
import os
import socket
import unittest
from pathlib import Path
from .offline_guard import no_network

def main():
    for flag in ("RUN_AI_INTEGRATION","RUN_OLLAMA_INTEGRATION"):
        os.environ.pop(flag,None)
    tests=Path(__file__).resolve().parents[2]/"tests"
    suite=unittest.defaultTestLoader.discover(str(tests),pattern="test_*.py")
    with no_network():
        result=unittest.TextTestRunner(verbosity=2).run(suite)
    summary=dict(tests_run=result.testsRun,passed=result.testsRun-len(result.errors)-len(result.failures)-len(result.skipped),
                 skipped=len(result.skipped),failures=len(result.failures),errors=len(result.errors),
                 live_calls_allowed=False)
    reports=Path(__file__).parent/"reports"
    reports.mkdir(exist_ok=True)
    (reports/"offline-tests.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    return 0 if result.wasSuccessful() else 1

if __name__=="__main__":
    raise SystemExit(main())
