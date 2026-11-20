"""Opt-in, provider-compatible terminal chat. No tools or command execution."""

from __future__ import annotations

import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def main() -> None:
    api_key = os.environ.get("LUX_AI_API_KEY")
    if not api_key:
        print("Set LUX_AI_API_KEY for your chosen OpenAI-compatible provider.", file=sys.stderr)
        raise SystemExit(2)
    base_url = os.environ.get("LUX_AI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    model = os.environ.get("LUX_AI_MODEL", "gpt-4o-mini")
    messages = [{"role": "system", "content": "You are Lux Assistant, a helpful conversational AI. Do not claim to access files, tools, or live information."}]
    print("Lux Assistant — chat is sent to your configured provider. Type /exit to quit.")
    while True:
        try:
            text = input("you> ").strip()
        except EOFError:
            print()
            return
        if text == "/exit":
            return
        if not text:
            continue
        messages.append({"role": "user", "content": text})
        payload = json.dumps({"model": model, "messages": messages}).encode("utf-8")
        request = Request(
            f"{base_url}/chat/completions", data=payload,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=60) as response:
                data = json.loads(response.read().decode("utf-8"))
            answer = data["choices"][0]["message"]["content"]
            if not isinstance(answer, str):
                raise ValueError("provider returned a non-text response")
        except (HTTPError, URLError, TimeoutError, KeyError, IndexError, ValueError, json.JSONDecodeError) as exc:
            messages.pop()
            print(f"assistant: request failed: {exc}", file=sys.stderr)
            continue
        messages.append({"role": "assistant", "content": answer})
        print(f"assistant> {answer}")


if __name__ == "__main__":
    main()
