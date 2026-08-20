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
echo "WEBUI_SECRET_KEY=$(openssl rand -base64 24)" > .env   # dev.sh needs one; unlike start.sh it won't generate it
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt -U
sh dev.sh
```

Frontend at `http://localhost:5173`, backend at `http://localhost:8080`.

**Extra** — from a clone of [extra-org/extra](https://github.com/extra-org/extra):

```bash
cp extra/.env.example extra/.env   # fill in the keys — see Environment below
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

`extra/.env`, for the dev setup above:

| Key | Value | Why |
| --- | --- | --- |
| `ANTHROPIC_API_KEY` | your key | the model the agents run on |
| `OPEN_WEBUI_URL` | `http://localhost:8080` | the backend, where tool calls actually land |
| `AGENT_AUTH_SECRET` | the same value as `backend/.env`'s `WEBUI_SECRET_KEY` | Extra verifies Open WebUI's session JWT itself — same secret, both sides |
| `AGENT_AUTH_MODE` | `host_token` | verify that JWT directly, no separate token-minting step |
| `AGENT_AUTH_CLAIM_USER_ID` | `id` | Open WebUI's token carries the user id under `id`, not the usual `sub` |
| `CORS_ORIGINS` | `http://localhost:5173` | where the browser loads the page from, not where the backend answers — the two are different ports in dev |

Get these wrong and the failure is specific enough to point back here: a
mismatched `AGENT_AUTH_SECRET` fails every request with a signature error, a
wrong `CORS_ORIGINS` shows up as a browser console error before any request
lands at all.

## What's in `extra/`

Three commits, each a step in the same story: a naive assistant sharing one admin API key between every user, then made to act as the caller instead, then made to survive runs longer than a session token's lifetime. Read them in order — `git log extra/` — to see why each change was needed, not just what it does.

`backend/open_webui/routers/auths.py` and the four files under `src/` are the Open WebUI side of the wiring: one endpoint that mints a short-lived token for the signed-in user, and the widget embed that calls it.
