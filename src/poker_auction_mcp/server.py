"""MCP server exposing the poker-auction game as tools for an AI agent.

The agent acts as a player: it joins a lobby with a chosen name, then observes
state changes (screen transitions, hole cards, current bid, shop offerings) and
takes actions (ready, bid, accept dutch offer, select card, buy joker).

Protocol mirrors src/lib/socket.ts from the poker-auction-client repo:
  - Outgoing events listed in FLAT_EVENTS are sent raw.
  - All other outgoing events are wrapped as {data, from, to}.
  - Incoming payloads are unwrapped: if payload.data exists, that is the arg.
"""

from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import urlparse, parse_qs

import socketio
from mcp.server.fastmcp import FastMCP

FLAT_EVENTS = {"join-lobby", "request-rejoin", "player-rejoined-as"}

# Production defaults (overridable via env vars in the MCP config).
DEFAULT_WS_URL = "wss://game-lobby-server.fly.dev"
DEFAULT_API_URL = "https://game-lobby-server.fly.dev/api/lobbies"


@dataclass
class GameState:
    connected: bool = False
    player_id: str | None = None
    lobby_id: str | None = None
    name: str = ""
    color: str = ""
    balance: int = 0
    rounds_won: int = 0
    hole_cards: list[dict] = field(default_factory=list)
    jokers: list[dict] = field(default_factory=list)
    screen: str | None = None
    loading_message: str | None = None
    current_bid: int = 0
    lots: list[dict] = field(default_factory=list)
    shop: list[dict] = field(default_factory=list)
    bonus: int = 0
    players: list[dict] = field(default_factory=list)
    notifications: list[dict] = field(default_factory=list)
    seq: int = 0  # bumped on every mutation so wait_for_update can detect changes

    def snapshot(self) -> dict[str, Any]:
        return {
            "connected": self.connected,
            "player_id": self.player_id,
            "lobby_id": self.lobby_id,
            "name": self.name,
            "color": self.color,
            "balance": self.balance,
            "rounds_won": self.rounds_won,
            "hole_cards": self.hole_cards,
            "jokers": self.jokers,
            "screen": self.screen,
            "loading_message": self.loading_message,
            "current_bid": self.current_bid,
            "lots": self.lots,
            "shop": self.shop,
            "bonus": self.bonus,
            "players": self.players,
            "pending_notifications": len(self.notifications),
            "seq": self.seq,
        }


class GameClient:
    """Socket.io client that mirrors the browser client's wire format."""

    def __init__(self) -> None:
        self.sio = socketio.AsyncClient(
            reconnection=True,
            reconnection_attempts=10,
            reconnection_delay=1,
            reconnection_delay_max=10,
        )
        self.state = GameState()
        self.update_event = asyncio.Event()
        self.joined_event = asyncio.Event()
        self._register_handlers()

    # --- helpers ---------------------------------------------------------

    def _bump(self) -> None:
        self.state.seq += 1
        self.update_event.set()

    def _register_handlers(self) -> None:
        sio = self.sio

        @sio.event
        async def connect():
            self.state.connected = True
            self._bump()

        @sio.event
        async def disconnect():
            self.state.connected = False
            self._bump()

        @sio.on("*")
        async def catch_all(event: str, payload: Any = None):
            # System events arrive flat; routed events wrap inner data.
            arg = payload.get("data") if isinstance(payload, dict) and "data" in payload else payload
            await self._handle_event(event, arg, payload)

    async def _handle_event(self, event: str, arg: Any, raw: Any) -> None:
        s = self.state
        if event == "connected":
            if isinstance(raw, dict):
                s.player_id = raw.get("from") or s.player_id
        elif event == "reconnected":
            if isinstance(raw, dict):
                s.player_id = raw.get("from") or s.player_id
                s.lobby_id = raw.get("lobbyId") or s.lobby_id
        elif event == "joined-lobby":
            if isinstance(arg, dict):
                s.lobby_id = arg.get("lobbyId") or s.lobby_id
                s.player_id = arg.get("clientId") or s.player_id
            self.joined_event.set()
        elif event == "player-joined-lobby":
            if isinstance(arg, dict):
                s.player_id = arg.get("id") or s.player_id
                s.color = arg.get("color") or s.color
            s.screen = "waiting-room"
        elif event == "change-screen":
            if isinstance(arg, dict):
                s.screen = arg.get("screen") or s.screen
                if s.screen == "loading":
                    s.loading_message = arg.get("message") or "Loading..."
                else:
                    s.loading_message = None
                if "bonus" in arg:
                    s.bonus = arg.get("bonus") or 0
                if "cards" in arg:
                    s.lots = arg.get("cards") or []
                if "hole_cards" in arg:
                    s.hole_cards = arg.get("hole_cards") or []
                if "jokers" in arg and s.screen == "hole-cards":
                    s.jokers = arg.get("jokers") or []
                if "jokers" in arg and s.screen == "shop":
                    s.shop = arg.get("jokers") or []
        elif event == "current-bid":
            if isinstance(arg, dict):
                s.current_bid = arg.get("current_bid") or 0
        elif event == "update-finance":
            if isinstance(arg, dict):
                s.balance = arg.get("balance") or 0
        elif event == "update-player":
            if isinstance(arg, dict):
                s.player_id = arg.get("id") or s.player_id
                s.lobby_id = arg.get("lobbyId") or s.lobby_id
                s.name = arg.get("name") or s.name
                s.color = arg.get("color") or s.color
                s.balance = arg.get("balance") or 0
                s.rounds_won = arg.get("rounds_won") or 0
                s.hole_cards = arg.get("hole_cards") or []
                s.jokers = arg.get("jokers") or []
        elif event == "update-player-state":
            if isinstance(arg, dict):
                if arg.get("id"): s.player_id = arg["id"]
                if arg.get("name"): s.name = arg["name"]
                if arg.get("color"): s.color = arg["color"]
                if arg.get("rounds_won") is not None: s.rounds_won = arg["rounds_won"]
                if arg.get("balance") is not None: s.balance = arg["balance"]
                if arg.get("hole_cards"): s.hole_cards = arg["hole_cards"]
                if arg.get("jokers"): s.jokers = arg["jokers"]
        elif event == "update-players-list":
            if isinstance(arg, dict):
                s.players = arg.get("players") or []
        elif event == "update-jokers":
            if isinstance(arg, dict):
                s.jokers = arg.get("jokers") or []
        elif event in ("allowed-joker", "forbid-joker"):
            if isinstance(arg, dict):
                joker = arg.get("joker") or {}
                key = joker.get("key")
                allowed = event == "allowed-joker"
                for j in s.jokers:
                    if j.get("key") == key:
                        j["allowed"] = allowed
        elif event == "new-message":
            if isinstance(arg, dict):
                s.notifications.append({"message": arg.get("message"), "author": arg.get("author")})
        elif event == "lobby-not-found":
            s.notifications.append({"message": "lobby-not-found", "author": "system"})
        self._bump()

    # --- outgoing --------------------------------------------------------

    async def emit(self, event: str, data: dict | None = None, to: str | None = None) -> None:
        if not self.sio.connected:
            raise RuntimeError("Not connected to game server. Call join_lobby first.")
        if event in FLAT_EVENTS:
            await self.sio.emit(event, data or {})
            return
        payload = {"data": data or {}, "from": self.state.player_id, "to": to}
        await self.sio.emit(event, payload)

    async def connect_with_auth(self, server_url: str) -> None:
        # The JS client sends {clientId} every (re)connect attempt. python-socketio
        # exposes `auth` as a one-shot value on connect(), which is enough for the
        # first connect; reconnects will reuse it. Initial clientId is None until
        # the server replies with `connected`.
        await self.sio.connect(
            server_url,
            auth={"clientId": self.state.player_id},
            transports=["websocket", "polling"],
            wait_timeout=10,
        )

    async def disconnect(self) -> None:
        if self.sio.connected:
            await self.sio.disconnect()


# --- MCP wiring -------------------------------------------------------------

mcp = FastMCP("poker-auction")
client = GameClient()

# Bundled rules file lives next to this module so it ships with the wheel.
_RULES_PATH = Path(__file__).with_name("rules.md")
_FALLBACK_RULES = (
    "# Bargain Poker\n\n"
    "A multiplayer poker game where you bid in auctions to decide which cards "
    "land on the shared board. Each round you get private hole cards plus 50 "
    "credits; you spend credits winning 3-card lots (via open, silent, or dutch "
    "auctions) and buying single-use jokers. The auction winner picks which lot "
    "cards become community cards. After all auction cycles, the best 5-card "
    "poker hand (2 hole cards + community cards) wins the round; first to 3 "
    "rounds wins the game.\n\n"
    "(Full rules file could not be loaded.)"
)


def _load_rules() -> str:
    """Return the bundled Bargain Poker rules, or a short fallback if the file
    can't be read."""
    try:
        return _RULES_PATH.read_text(encoding="utf-8")
    except OSError:
        return _FALLBACK_RULES


@mcp.resource("game://rules", name="game-rules", mime_type="text/markdown")
def game_rules() -> str:
    """The rules of Bargain Poker: objective, round flow, the three auction
    formats (open / silent / dutch), jokers, and the credit economy. Read this
    to learn how to play before taking actions."""
    return _load_rules()


def _extract_lobby_id(lobby_url_or_id: str) -> str:
    """Accept either a raw lobby id or a frontend URL like
    `http://host:5173/lobby?lobbyId=ABC123`."""
    if "?" in lobby_url_or_id or "://" in lobby_url_or_id or "/" in lobby_url_or_id:
        parsed = urlparse(lobby_url_or_id)
        qs = parse_qs(parsed.query)
        if "lobbyId" in qs and qs["lobbyId"]:
            return qs["lobbyId"][0]
        # Fallback: last non-empty path segment.
        segments = [seg for seg in parsed.path.split("/") if seg]
        if segments:
            return segments[-1]
    return lobby_url_or_id.strip()


@mcp.tool()
async def join_lobby(
    lobby_url_or_id: str,
    player_name: str,
    server_url: str | None = None,
) -> dict:
    """Connect to the game server and join a lobby as a new player.

    Args:
        lobby_url_or_id: Either the lobby URL the game master shared
            (e.g. http://localhost:5173/lobby?lobbyId=ABC123) or just the lobby id.
        player_name: The display name this agent will use at the table.
        server_url: Optional override for the socket.io server URL. If omitted,
            uses the POKER_SERVER_URL environment variable.

    Returns the current game state after the join handshake completes.
    """
    url = server_url or os.environ.get("POKER_SERVER_URL") or DEFAULT_WS_URL
    lobby_id = _extract_lobby_id(lobby_url_or_id)
    client.state.name = player_name

    if not client.sio.connected:
        await client.connect_with_auth(url)

    client.joined_event.clear()
    await client.sio.emit("join-lobby", {"lobbyId": lobby_id, "name": player_name})
    try:
        await asyncio.wait_for(client.joined_event.wait(), timeout=10)
    except asyncio.TimeoutError:
        raise RuntimeError("Timed out waiting for joined-lobby ack from server.")

    # JS client emits `new-player` immediately after joined-lobby ack to register name.
    await client.emit("new-player", {"name": player_name})
    # Give the server a moment to broadcast player-joined-lobby / update-player.
    try:
        await asyncio.wait_for(client.update_event.wait(), timeout=2)
    except asyncio.TimeoutError:
        pass
    client.update_event.clear()
    return client.state.snapshot()


@mcp.tool()
async def get_game_rules() -> str:
    """Return the rules of Bargain Poker as markdown: the objective, round flow,
    the three auction formats (open / silent / dutch), jokers, and the credit
    economy. Call this FIRST, before joining or taking any action, so you know
    how to play. Same content as the `game://rules` resource."""
    return _load_rules()


@mcp.tool()
async def get_state() -> dict:
    """Return the current observable game state: screen, balance, hole cards,
    jokers, current bid, available lots (cards to pick), shop offerings, and
    a monotonic `seq` counter you can pass to wait_for_update."""
    return client.state.snapshot()


@mcp.tool()
async def wait_for_update(
    timeout_seconds: float = 30.0,
    until_screen: str | None = None,
    since_seq: int | None = None,
) -> dict:
    """Block until the game state changes, then return the new snapshot.

    Use this after taking an action (or after joining) to wait for the server's
    next event — a screen change, a new bid, an updated balance, etc.

    Args:
        timeout_seconds: Max time to wait. Returns current state on timeout.
        until_screen: If set, keep waiting until state.screen == this value.
        since_seq: If set, return as soon as state.seq > since_seq.
            Pass the `seq` from your last get_state to avoid missing fast updates.
    """
    if since_seq is not None and client.state.seq > since_seq:
        return client.state.snapshot()
    if until_screen is not None and client.state.screen == until_screen:
        return client.state.snapshot()

    deadline = asyncio.get_event_loop().time() + timeout_seconds
    while True:
        remaining = deadline - asyncio.get_event_loop().time()
        if remaining <= 0:
            break
        client.update_event.clear()
        try:
            await asyncio.wait_for(client.update_event.wait(), timeout=remaining)
        except asyncio.TimeoutError:
            break
        if until_screen is not None:
            if client.state.screen == until_screen:
                break
            continue
        if since_seq is not None:
            if client.state.seq > since_seq:
                break
            continue
        break
    return client.state.snapshot()


@mcp.tool()
async def ready() -> dict:
    """Signal that the agent is ready to proceed. Used in the waiting room
    (to start the game) and after viewing dealt hole cards."""
    await client.emit("ready", {})
    return client.state.snapshot()


@mcp.tool()
async def place_bid(amount: int) -> dict:
    """Submit a bid in an open or silent auction. `amount` is in chips.
    Check get_state() — screen should be 'open-auction' or 'silent-auction',
    and current_bid tells you what to beat in open auctions."""
    if amount <= 0:
        raise ValueError("Bid amount must be positive.")
    await client.emit("new-bid", {"amount": amount})
    return client.state.snapshot()


@mcp.tool()
async def accept_dutch_offer() -> dict:
    """Buy at the current price in a dutch auction (screen == 'dutch-auction').
    Whoever clicks first wins the lot at the displayed price, which drops over
    time until someone accepts."""
    await client.emit("new-offer", {})
    return client.state.snapshot()


@mcp.tool()
async def select_card(suit: str, rank: str) -> dict:
    """Pick one of the community/lot cards (screen == 'card-select').
    The valid choices are in state.lots — pass the suit and rank of one of them."""
    match = None
    for card in client.state.lots:
        if str(card.get("suit")) == str(suit) and str(card.get("rank")) == str(rank):
            match = card
            break
    if match is None:
        available = [(c.get("suit"), c.get("rank")) for c in client.state.lots]
        raise ValueError(f"Card {suit} {rank} not in current lots. Available: {available}")
    await client.emit("select-card", {"card": match})
    return client.state.snapshot()


@mcp.tool()
async def buy_joker(key: str) -> dict:
    """Buy a joker from the shop (screen == 'shop'). `key` must match one of
    the entries in state.shop. Cost is deducted from balance by the server."""
    keys = [j.get("key") for j in client.state.shop]
    if key not in keys:
        raise ValueError(f"Joker '{key}' not on offer. Available: {keys}")
    await client.emit("buy", {"key": key})
    return client.state.snapshot()


@mcp.tool()
async def get_notifications(clear: bool = True) -> list[dict]:
    """Drain queued chat/system notifications received from the server."""
    items = list(client.state.notifications)
    if clear:
        client.state.notifications.clear()
    return items


@mcp.tool()
async def disconnect_from_game() -> dict:
    """Disconnect from the game server. Use when the agent is done playing."""
    await client.disconnect()
    return client.state.snapshot()


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
