"""Manual real HTTP smoke check; launches and stops an isolated backend server."""
import socket
import subprocess
import sys
import time
from pathlib import Path

import httpx


def main():
    backend = Path(__file__).resolve().parents[1] / "backend"
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    server = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(port)],
        cwd=backend, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        with httpx.Client(base_url=f"http://127.0.0.1:{port}", timeout=130, trust_env=False) as client:
            for attempt in range(50):
                if server.poll() is not None:
                    raise RuntimeError("Backend exited before readiness.")
                try:
                    health = client.get("/health")
                    health.raise_for_status()
                    break
                except httpx.ConnectError:
                    time.sleep(0.1)
            else:
                raise RuntimeError("Backend did not become ready.")
            response = client.post("/api/embeddings/test", json={"text": "The supplier must notify the company within 48 hours."})
            print(f"Real HTTP endpoint: {response.status_code} {response.json()}")
            response.raise_for_status()
            payload = response.json()
            assert set(payload) == {"success", "model", "dimensions"}
            assert payload["success"] is True and payload["dimensions"] > 0
            print(f"Health: {health.status_code} {health.json()}")
    finally:
        server.terminate()
        try:
            server.wait(timeout=10)
        except subprocess.TimeoutExpired:
            server.kill()
            server.wait(timeout=10)


if __name__ == "__main__":
    main()
