# Open WebUI + Extra

This is [Open WebUI](https://github.com/open-webui/open-webui) with an [Extra](https://github.com/extra-org/extra) assistant embedded in it, wired to act as whoever is signed in rather than through one shared admin key. Everything Extra-specific lives in [`extra/`](extra/); the rest is upstream Open WebUI ([its own README](README.upstream.md)).

## Run it

**Open WebUI** — two terminals, per the [official dev guide](https://docs.openwebui.com/getting-started/advanced-topics/development):

```bash
# terminal 1 — frontend
cp -RPp .env.example .env
npm install
npm run build
npm run dev
```

```bash
# terminal 2 — backend
cd backend
cp .env.example .env   # dev.sh needs WEBUI_SECRET_KEY set; unlike start.sh it won't generate one
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt -U
sh dev.sh
```

Frontend at `http://localhost:5173`, backend at `http://localhost:8080`.

**Extra** — set up `extra/.env` per the Environment section below, then from a clone of [extra-org/extra](https://github.com/extra-org/extra):

```bash
make dev AGENTS=<path-to-this-repo>/extra/agents.yml ENV_FILE=<path-to-this-repo>/extra/.env
```

Or with Docker instead of a local `extra` checkout:

```bash
docker run -d -p 8100:8100 \
  -v <path-to-this-repo>/extra:/workspace -w /workspace \
  --env-file <path-to-this-repo>/extra/.env \
  ghcr.io/extra-org/extra:latest \
  agent-manager --config agents.yml --port 8100
```

Playground at `http://localhost:8100/playground`. Sign into Open WebUI and the assistant appears there too.

## Environment

```bash
cp extra/.env.example extra/.env
```

Everything below is already filled in except the model key — open `extra/.env` and add that, and you're running:

```bash
ANTHROPIC_API_KEY=your-key-here   # or see the Ollama comment for a free local model instead

OPEN_WEBUI_URL=http://localhost:8080

AGENT_AUTH_MODE=host_token
AGENT_AUTH_SECRET=pLiUxoi+ziwTUIhNhVg/AN1U50UMom00
AGENT_AUTH_CLAIM_USER_ID=id

CORS_ORIGINS=http://localhost:5173
```

What each of these is, and why it has to be that exact value:

| Key | Value | Why |
| --- | --- | --- |
| `ANTHROPIC_API_KEY` | your key | the model the agents run on — skip it and use [Ollama](https://ollama.com) for free instead, see the comment above |
| `OPEN_WEBUI_URL` | `http://localhost:8080` | the backend, where tool calls actually land |
| `AGENT_AUTH_SECRET` | `pLiUxoi+ziwTUIhNhVg/AN1U50UMom00` — same fixed value as `backend/.env.example`'s `WEBUI_SECRET_KEY` | Extra verifies Open WebUI's session JWT itself; HMAC means one shared secret signs and verifies on both sides |
| `AGENT_AUTH_MODE` | `host_token` | verify that JWT directly, no separate token-minting step |
| `AGENT_AUTH_CLAIM_USER_ID` | `id` | Open WebUI's token carries the user id under `id`, not the usual `sub` |
| `CORS_ORIGINS` | `http://localhost:5173` | where the browser loads the page from, not where the backend answers — the two are different ports in dev |

`AGENT_AUTH_SECRET`/`WEBUI_SECRET_KEY` is a fixed, publicly-known dev value —
the same one ships in both `.env.example` files, on purpose. That's fine only
because this all runs on your machine with no real users and nothing else
trusts it; change both together to something private (`openssl rand -base64
24`) the moment this runs anywhere else reachable.

Get the rest wrong and the failure points back here: a mismatched
`AGENT_AUTH_SECRET` fails every request with a signature error, a wrong
`CORS_ORIGINS` shows up as a browser console error before any request lands
at all.

## What's in `extra/`

Three commits, each a step in the same story: a naive assistant sharing one admin API key between every user, then made to act as the caller instead, then made to survive runs longer than a session token's lifetime. Read them in order — `git log extra/` — to see why each change was needed, not just what it does.

`backend/open_webui/routers/auths.py` and the four files under `src/` are the Open WebUI side of the wiring: one endpoint that mints a short-lived token for the signed-in user, and the widget embed that calls it.
