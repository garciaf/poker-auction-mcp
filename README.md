# poker-auction-mcp

A local MCP server that lets an AI agent (Claude Code, Claude Desktop, etc.) join and play the [poker-auction-client](../poker-auction-client) game as a player.

The agent connects to the same socket.io game server your game master is running, joins a lobby with a chosen name, and gets the same state stream the browser UI would receive — then takes actions through MCP tools.

## How it fits together

```
game master  ──▶  game server (socket.io)  ◀──  browser players (human)
                       ▲
                       └──  poker-auction-mcp  ◀──  AI agent (Claude)
```

## Install

```bash
cd ~/Development/poker-auction-mcp
uv sync          # or: pip install -e .
```

Requires Python 3.10+.

## Register with Claude Code

Add to your Claude Code MCP config (`~/.claude/mcp.json` or via `claude mcp add`):

```json
{
  "mcpServers": {
    "poker-auction": {
      "command": "uv",
      "args": ["--directory", "/Users/YOU/Development/poker-auction-mcp", "run", "poker-auction-mcp"]
    }
  }
}
```

By default the MCP connects to the **production** game server:

- WebSocket (socket.io): `wss://game-lobby-server.fly.dev`
- REST lobby API: `https://game-lobby-server.fly.dev/api/lobbies`

Override either with env vars in the MCP config if you want to point at a local dev server instead:

```json
"env": {
  "POKER_SERVER_URL": "http://localhost:3000",
  "POKER_API_URL": "http://localhost:3000/api/lobbies"
}
```

## Tools exposed

| Tool | When to call | What it does |
|------|--------------|--------------|
| `get_game_rules()` | First, before joining | Returns the full Bargain Poker rules as markdown (same content as the `game://rules` resource). Call this so the agent knows how to play before acting. |
| `join_lobby(lobby_url_or_id, player_name, server_url?)` | Once, at the start | Connects to the server, joins the lobby, registers a player name. Accepts the full frontend URL (parses `?lobbyId=…`) or a bare id. |
| `fetch_game_state(wait_seconds?, timeout_seconds?)` | After every action and whenever waiting | Asks the host for the authoritative game state AND a 320×180 screenshot of the viewport. Returns both as separate content blocks so the LLM can read the structured state and see the game. `wait_seconds` (default `0`, capped at `30`) sleeps before the request — set higher when waiting for others to act (e.g. `10` right after joining). |
| `ready()` | Waiting room & after viewing hole cards | Emits `ready` — moves the game forward. |
| `place_bid(amount)` | `screen == 'open-auction'` or `'silent-auction'` | Submits a bid. |
| `accept_dutch_offer()` | `screen == 'dutch-auction'` | Buys at the currently displayed (descending) price. |
| `select_card(suit, rank)` | `screen == 'card-select'` | Picks one of the cards in `state.lots`. |
| `buy_joker(key)` | `screen == 'shop'` | Buys a joker (key must match one in `state.shop`). |
| `get_notifications(clear?)` | Anytime | Drains queued chat / system messages. |
| `disconnect_from_game()` | When done | Closes the socket. |

## Resources exposed

| Resource | What it returns |
|----------|-----------------|
| `game://rules` | The full Bargain Poker rules (objective, round flow, the three auction formats, jokers, credit economy). Served from [src/poker_auction_mcp/rules.md](src/poker_auction_mcp/rules.md). An agent should read this before playing. |
| `poker-auction://playbook` | The agent playbook: perception/action loop, per-screen decision table, silent-auction bidding strategy, common mistakes. Same content is auto-shipped to the LLM via the server's `instructions` field on `initialize`; this resource is for explicit re-attachment. |

## Typical agent flow

1. `get_game_rules()` — learn the rules of Bargain Poker.
2. `join_lobby("http://localhost:5173/lobby?lobbyId=ABC123", "Claudius")`.
3. `fetch_game_state(wait_seconds=10)` — give the game master time to start the round, then look at the structured state + screenshot.
4. Act based on `state.screen`:
   - `waiting-room` / `hole-cards` → `ready()`
   - `silent-auction` → `place_bid(amount)` (exactly once)
   - `open-auction` → `place_bid(amount)`
   - `dutch-auction` → `accept_dutch_offer()`
   - `card-select` → `select_card(suit, rank)` from `state.lots`
   - `shop` → optionally `buy_joker(key)`
   - `finance` / `loading` → observe, no action
5. `fetch_game_state(wait_seconds=0)` after each action; if the screen hasn't changed yet, call again with a higher `wait_seconds` (up to 30) until something moves. Loop.

## Game rules

The canonical game rules live in **[src/poker_auction_mcp/rules.md](src/poker_auction_mcp/rules.md)** and are served to agents through the `game://rules` MCP resource (see *Resources exposed* above).

> Edit the rules in `rules.md`, not here — that file is what the agent actually reads. This keeps the rules a deliberate, self-contained artifact rather than something that drifts when these docs are reworded.

---

# Development & Deployment

## Debug WebSocket Events

These events are intended for development tooling only (e.g. the debug bar in the client app). They are not part of the game flow.

### `screenshot-requested` → `screenshot`

Request a screenshot of the current game viewport.

**Client emits:** `screenshot-requested` (no payload)

**Server responds with:** `screenshot`

| Field | Type | Description |
|---|---|---|
| `image` | `string` | JPEG image encoded as a base64 string (320×180, quality 0.6) |

```json
{ "image": "<base64-encoded-jpeg>" }
```

> The server waits for the current frame to finish rendering (`RenderingServer.frame_post_draw`) before capturing, so the screenshot always reflects the latest drawn frame.

---

### `game-state-requested` → `game-state-update`

Request the full game state for the calling player.

**Client emits:** `game-state-requested` (no payload)

**Server responds with:** `game-state-update`

Payload is the full `GameManager.get_game_state_for_player()` dictionary plus a `current_screen` key indicating which screen the player is currently on.



## Publishing (later)

When you want one-line install like Playwright MCP, publish to PyPI and users can run `uvx poker-auction-mcp`. For now, local `uv run` works the same way and needs no publishing.
