# Bot Development Plan

## 1. Scaffold and Architecture

The primary goal is to build a testable architecture. We will separate the Telegram transport layer from the core business logic. The logic will reside in the `handlers` directory as pure Python functions that take strings and return strings. The `bot.py` entry point will support a `--test` CLI flag to execute these handlers directly via stdout, bypassing the Telegram API entirely.

## 2. Backend Integration

Once the scaffold is verified, we will implement the `services/` layer. This will use the `httpx` library to communicate with the LMS backend using the credentials provided in `.env.bot.secret`. Handlers like `/health` and `/labs` will be updated to fetch real data from the backend instead of returning placeholder text.

## 3. Intent Routing (LLM)

For free-form queries (e.g., "what labs are available"), we will integrate an LLM client. We will implement an intent classifier that decides whether the user is executing a strict command or asking a natural language question. The LLM will parse the user's intent and map it to the corresponding backend service function.

## 4. Deployment

The bot will be deployed on the provided VM using standard Linux background processes (`nohup`). We will ensure all environment variables are securely stored in `.env.bot.secret` on the VM and not committed to version control.
