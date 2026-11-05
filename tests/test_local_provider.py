import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from ainoise.cli import main
from ainoise.noise import generate
from ainoise.providers import LocalProvider
from ainoise.runner import load_runs, run_experiment


class FakeServer:
    """A tiny OpenAI-compatible server, like Ollama's /v1 endpoint."""

    def __init__(self, content, models=("tiny-llm:1b",), extra_message=None):
        self.requests = []
        outer = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def _send(self, body):
                raw = json.dumps(body).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(raw)))
                self.end_headers()
                self.wfile.write(raw)

            def do_GET(self):
                outer.requests.append(("GET", self.path, None, dict(self.headers)))
                self._send({"data": [{"id": m} for m in models]})

            def do_POST(self):
                body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                outer.requests.append(("POST", self.path, body, dict(self.headers)))
                message = {"role": "assistant", "content": content, **(extra_message or {})}
                self._send({
                    "model": body["model"],
                    "choices": [{"message": message, "finish_reason": "stop"}],
                    "usage": {"prompt_tokens": 12, "completion_tokens": 34},
                })

        self.httpd = HTTPServer(("127.0.0.1", 0), Handler)
        self.url = f"http://127.0.0.1:{self.httpd.server_port}/v1"
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()

    def close(self):
        self.httpd.shutdown()


@pytest.fixture
def server():
    servers = []

    def make(*args, **kwargs):
        s = FakeServer(*args, **kwargs)
        servers.append(s)
        return s

    yield make
    for s in servers:
        s.close()


def test_local_provider_sends_only_noise_and_records_model(server, tmp_path):
    srv = server("<think>hmm, gibberish</think>\n```python\nprint('hi')\n```")
    provider = LocalProvider(base_url=srv.url)
    assert provider.model == "tiny-llm:1b"  # first model the server lists

    n = generate("keysmash", 50, seed=4)
    run_dir = run_experiment("code", n, provider, tmp_path)
    _, path, body, headers = srv.requests[-1]
    assert path == "/v1/chat/completions"
    assert body["messages"][1] == {"role": "user", "content": n.text}
    assert "Authorization" not in headers

    record = load_runs(tmp_path)[0]
    assert (record["provider"], record["model"]) == ("local", "tiny-llm:1b")
    assert record["stop_reason"] == "end_turn"
    assert record["usage"] == {"input_tokens": 12, "output_tokens": 34}
    assert record["reasoning"] == "hmm, gibberish"
    assert record["artifact"]["kind"] == "code"
    assert "<think>" not in (run_dir / "response.md").read_text()
    assert run_dir.name.endswith("-tiny-llm-1b")


def test_local_provider_reasoning_field_and_api_key(server):
    srv = server("plain words", extra_message={"reasoning_content": "thinking..."})
    provider = LocalProvider(model="m", base_url=srv.url + "/", api_key="sk-x")
    c = provider.complete("sys", "noise")
    assert (c.text, c.reasoning, c.model) == ("plain words", "thinking...", "m")
    assert srv.requests[-1][3]["Authorization"] == "Bearer sk-x"


def test_local_provider_unreachable_is_a_clear_error():
    with pytest.raises(RuntimeError, match="could not reach a model server"):
        LocalProvider(base_url="http://127.0.0.1:9/v1", timeout=2)


def test_same_noise_two_models_side_by_side(server, tmp_path):
    a, b = server("# A", models=("llama3.2",)), server("# B", models=("qwen3:8b",))
    args = ["run", "--task", "text", "--provider", "local", "--seed", "7",
            "--results-dir", str(tmp_path / "r"), "--docs-dir", str(tmp_path / "d"),
            "--readme", str(tmp_path / "none.md")]
    assert main([*args, "--base-url", a.url]) == 0
    assert main([*args, "--base-url", b.url]) == 0
    runs = load_runs(tmp_path / "r")
    assert sorted(r["model"] for r in runs) == ["llama3.2", "qwen3:8b"]
    page = (tmp_path / "d" / "index.html").read_text()
    assert 'data-model="qwen3:8b"' in page and 'data-value="llama3.2"' in page
