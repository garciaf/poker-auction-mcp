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
| `get_state()` | Anytime | Returns the full observable snapshot (screen, balance, hole_cards, jokers, current_bid, lots, shop, seq, …). |
| `wait_for_update(timeout_seconds?, until_screen?, since_seq?)` | After any action | Blocks until the server pushes a state change. Use `until_screen` to wait for a specific phase, or `since_seq` to wait for any change after the last snapshot you saw. |
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

## Typical agent flow

1. `join_lobby("http://localhost:5173/lobby?lobbyId=ABC123", "Claudius")`
2. `wait_for_update(until_screen="hole-cards")` — game master starts the round
3. Inspect `hole_cards`, then `ready()`
4. `wait_for_update()` — the next screen tells the agent what to do:
   - `open-auction` / `silent-auction` → `place_bid(amount)`
   - `dutch-auction` → `accept_dutch_offer()` when the price is right
   - `card-select` → `select_card(suit, rank)` from `state.lots`
   - `shop` → optionally `buy_joker(key)`
   - `finance` → just observe `bonus`
5. Loop on `wait_for_update()` between actions.

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
