# How to play: poker-auction (silent-auction edition)

You are a player at a multi-round poker-auction table. Each round you receive
two private hole cards. Community cards are auctioned one at a time by **silent
auction** (sealed-bid, single shot, highest bid wins, losers see nothing). At
the end of each round, the best 5-card hand from `hole_cards + community_cards`
wins the round. First player to reach `max_victory` rounds wins overall.

## The perception/action loop

You only have one perception tool: `fetch_game_state`. It returns BOTH the
structured game state AND a screenshot of the host's viewport on every call.
Call it before every decision — it is always ground truth.

```
join_lobby(lobby_url_or_id, player_name)
[state, image] = fetch_game_state(wait_seconds=10)   # game master needs time to start
loop forever:
    act based on state.screen  (see decision table below)
    [state, image] = fetch_game_state(wait_seconds=?)
```

### How to choose `wait_seconds`

The default is `0` — fetch immediately. But increase it whenever you have
nothing useful to do but wait:

- **First call after `join_lobby`: use `10`.** The game master usually needs
  several seconds to start the round; fetching immediately just shows you the
  empty waiting room.
- **After an action when you've passed the turn to another player** (e.g.
  finished placing your silent bid): use `5–10`. Avoids spamming the server
  while opponents are still deciding.
- **You just fetched and the screen hasn't changed yet** — same screen, not
  your turn: bump `wait_seconds` up gradually (e.g. 5 → 10 → 20). Never above
  30. The tool will cap higher values at 30 anyway.
- **You just took an action and expect immediate progress** (e.g. `ready()`
  in waiting-room when you're the only one left): `1–2` is enough.
- **You want to look right now** (debugging, sanity check): `0`.

If you wait the full duration and the screen still hasn't changed, just call
`fetch_game_state` again with a larger wait. No need to escalate quickly.

## Decision table

| `state.screen` | What to do |
|----------------|------------|
| `waiting-room` | Call `ready()`. |
| `loading`      | Do nothing — just fetch again. |
| `hole-cards`   | Read `state.hole_cards`. Plan the round. Call `ready()`. |
| `silent-auction` | Decide your bid (see below). Call `place_bid(amount)` **exactly once**. |
| `card-select`  | Pick the card from `state.lots` (a.k.a. `state.cards_for_bidding`) that maximizes your hand value given current `hole_cards + community_cards`. Call `select_card(suit, rank)`. |
| `shop`         | Look at `state.shop`. If a joker is worth its `price`, call `buy_joker(key)`. To skip without buying, call `ready()` — that's how you signal you're done shopping. |
| `finance`      | Passive screen — observe `state.bonus`. |

After any action above, immediately call `fetch_game_state(wait_seconds=0)` to
see the result. Only add a wait time if the *next* fetch shows the same screen
you just acted on (meaning other players or the host haven't advanced yet).

## Silent-auction bidding strategy

A silent auction is blind: nobody sees competitors' bids. The `current_bid`
value in state is the **minimum** bid (floor), not a competing bid — ignore it
except as a lower bound.

A workable starting heuristic:

```
hand_strength = ...   # 0.0 to 1.0 based on hole_cards + revealed community
urgency       = round_number / max_victory     # ramps up over the match
max_bid       = floor(balance * hand_strength * (1 + urgency) / 2)
bid           = max(minimum_bid, max_bid)      # never below floor
```

**Hard rules**:
- Never bid above your `max_bid`.
- Never call `place_bid` twice in the same auction. If you've already bid,
  just wait for the screen to change.
- If `balance < 5`, bid the minimum and conserve chips for stronger hands.
- Stronger hands deserve disproportionately more — bid quadratically, not
  linearly, with `hand_strength`.

## Hand-strength quick guide

Rough 0–1 scale you can use until you have data:

- Pocket pair AA / KK / QQ: 0.9
- Pocket pair JJ / TT: 0.7
- Pocket pair 88-99: 0.55
- Suited connectors (T-9s+): 0.5
- Two high cards (AK, AQ, KQ): 0.6
- One ace + low kicker: 0.35
- Two unconnected low cards: 0.15

Once community cards start appearing, re-evaluate using actual made hands
(pair, two pair, straight draw, flush draw, …).

## Using the screenshot

Every `fetch_game_state` call returns a 320×180 JPEG of what the host sees.
Use it to:
- Verify the `screen` value matches what's actually on display.
- Spot animations or UI states the structured payload doesn't capture.
- Sanity-check before bidding (am I really in the auction screen?).

Don't make decisions purely from the image — the structured state is the
authoritative source. The image is for cross-checking and recovery.

## Common mistakes to avoid

1. Calling `place_bid` more than once per silent auction — you committed your
   number, that's final.
2. Calling `fetch_game_state` repeatedly with `wait_seconds=0` while the
   screen hasn't changed — spams the server. Increase `wait_seconds` (up to
   30) instead.
3. Bidding when `state.screen != "silent-auction"` — the call will be rejected
   or ignored. Always read screen first.
4. Selecting a card not in `state.lots` — only cards in the lots are valid.
5. Forgetting `ready()` after viewing hole cards — the game pauses on you.
