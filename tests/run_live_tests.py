"""Explicit opt-in runner: invokes real Ollama and Gemini services."""
import os
import unittest

os.environ["RUN_AI_INTEGRATION"] = "1"
os.environ["RUN_OLLAMA_INTEGRATION"] = "1"
if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.discover("tests"))
    raise SystemExit(not result.wasSuccessful())
