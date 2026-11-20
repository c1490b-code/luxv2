# Lux

Lux is an open-source project for a small, readable programming language, a terminal AI assistant, and an ecosystem of Lux apps. This repository is the first working foundation—not a claim that every planned feature is already implemented.

## What works today

- **Lux language:** run `.lux` scripts or use the REPL. The initial interpreter supports numbers, strings, booleans, `nil`, arithmetic, comparisons, variables, and built-ins (`print`, `len`, `str`, `int`, `type`).
- **Lux Assistant:** an opt-in terminal chat app that connects to an OpenAI-compatible chat-completions endpoint. It does not execute commands or access your files.
- **One install, two commands:** `lux` and `lux-assistant`.

## Install and try it

Requires Python 3.11 or later.

```bash
python -m pip install -e .
lux examples/hello.lux
lux
lux-assistant
```

Example Lux program:

```lux
let name = "world"
print("Hello, " + name + "!")
print(6 * 7)
```

The REPL accepts one statement per line. Type `exit` or press Ctrl-D to leave.

## Configure the assistant

Set credentials for the provider you choose; the assistant has no built-in key and makes no network requests until launched:

```bash
export LUX_AI_API_KEY="your-provider-key"
export LUX_AI_BASE_URL="https://api.openai.com/v1" # optional
export LUX_AI_MODEL="your-chat-model"              # optional
lux-assistant
```

The assistant sends your chat messages to the configured endpoint. Do not enter sensitive information unless you trust that provider. It does not have tools, browse the web, or run generated code. The provider must implement the OpenAI-compatible `/chat/completions` API.

## Development

```bash
python -m unittest discover -s tests -v
```

See [the language guide](docs/language.md), [assistant notes](apps/assistant/README.md), and [roadmap](ROADMAP.md).

## Project principles

Lux aims to be approachable, portable, privacy-conscious, and useful to both its creator and the people they choose to share it with. Features should be clearly labeled as implemented, experimental, or planned; no app should claim access to “everything” or silently act on a user's behalf.

## License

MIT. See [LICENSE](LICENSE).
