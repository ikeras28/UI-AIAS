"""
ai_engine.py
Módulo de conexión con Ollama (LLM local).
"""

import json
import requests
from typing import Callable

OLLAMA_BASE     = "http://localhost:11434"
OLLAMA_GENERATE = f"{OLLAMA_BASE}/api/generate"
OLLAMA_TAGS     = f"{OLLAMA_BASE}/api/tags"
DEFAULT_MODEL   = "llama3.2"
TIMEOUT         = 120


class OllamaConnectionError(Exception):
    pass


class AIEngine:

    def __init__(self, model: str = DEFAULT_MODEL):
        self.model = model

    def check_connection(self) -> bool:
        try:
            r = requests.get(OLLAMA_BASE, timeout=5)
            return r.status_code == 200
        except Exception:
            return False

    def list_models(self) -> list:
        try:
            r = requests.get(OLLAMA_TAGS, timeout=10)
            r.raise_for_status()
            models = [m["name"] for m in r.json().get("models", [])]
            return models if models else [DEFAULT_MODEL]
        except Exception:
            return [DEFAULT_MODEL]

    def stream_query(
        self,
        prompt: str,
        on_token: Callable[[str], None],
        on_done: Callable[[str], None] = None,
    ) -> None:
        if not self.check_connection():
            raise OllamaConnectionError(
                "Ollama no está activo.\n"
                "Busca el icono llama en la bandeja del sistema."
            )
        payload = {"model": self.model, "prompt": prompt, "stream": True}
        try:
            response = requests.post(
                OLLAMA_GENERATE, json=payload, stream=True, timeout=TIMEOUT)
            response.raise_for_status()
        except requests.exceptions.ConnectionError as e:
            raise OllamaConnectionError(f"No se pudo conectar con Ollama: {e}") from e
        except requests.exceptions.HTTPError as e:
            raise OllamaConnectionError(f"Error HTTP de Ollama: {e}") from e

        full_response = []
        for line in response.iter_lines():
            if not line:
                continue
            try:
                chunk = json.loads(line.decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue
            token = chunk.get("response", "")
            if token:
                full_response.append(token)
                on_token(token)
            if chunk.get("done", False):
                break

        if on_done:
            on_done("".join(full_response))

    def simple_query(self, prompt: str) -> str:
        if not self.check_connection():
            raise OllamaConnectionError("Ollama no está activo.")
        payload = {"model": self.model, "prompt": prompt, "stream": False}
        try:
            r = requests.post(OLLAMA_GENERATE, json=payload, timeout=TIMEOUT)
            r.raise_for_status()
            return r.json().get("response", "").strip()
        except Exception as e:
            raise OllamaConnectionError(f"Error: {e}") from e