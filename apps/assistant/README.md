# Lux Assistant

`lux-assistant` is a small terminal chat client shipped with the Lux starter kit. It uses Python's standard library and an OpenAI-compatible `/chat/completions` API.

## Setup

Set `LUX_AI_API_KEY` and optionally `LUX_AI_BASE_URL` and `LUX_AI_MODEL`, then run `lux-assistant`. The default endpoint and model are configurable and are not guaranteed to be available for every provider. Type `/exit` to leave.

## Privacy and safety

The app sends the chat transcript to the provider configured by the user. Review that provider's data policies; don't share secrets or sensitive personal information unless appropriate. Keep API keys in environment variables or a secrets manager, never in source code. The app does not browse, call tools, read local files, execute commands, or act autonomously. This is a chat client, not a model or a bundled AI service.
