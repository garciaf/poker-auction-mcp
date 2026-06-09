# Bargain Poker

A multiplayer poker game with a twist — you have to **bid to put cards on the table**.

Instead of community cards being revealed freely, players fight in auction wars to decide which cards make it to the board. Every card on the table was bought by someone. Every chip spent was a strategic choice.

## How to Play

### Setup
- The game runs on a shared desktop screen (TV or monitor)
- Each player joins on their **smartphone** by scanning a QR code shown on the main screen
- The game plays up to **5 rounds**; first player to win **3 rounds** wins the game (configurable 1–9 in settings)

### Each Round
1. **Hole Cards** — Every player is privately dealt 2 cards, visible only on their phone
2. **Auction Cycles** — The round consists of multiple auction cycles. Each cycle, 3 cards are presented as a lot for bidding
3. **Bidding** — Players compete to win the lot using one of three auction formats (see below)
4. **Card Selection** — The auction winner chooses which card(s) from the 3-card lot are added to the shared **community cards** on the table; the rest go back to the deck
5. **Hand Evaluation** — After all auction cycles, each player's best 5-card poker hand is compared (their 2 hole cards + all community cards). The best hand wins the round.

### Winning
- Win a round by holding the best poker hand at the end
- Win the game by winning the most rounds (default: first to 3)

---

## Poker Hand Rankings

Your final hand is the **best 5-card combination** you can make from your 2 private hole cards plus all the shared community cards on the table. At showdown, hands are compared and the **highest-ranked** hand wins the round.

Hands are ranked below from **strongest (10) to weakest (1)**. A higher rank always beats a lower rank, regardless of the individual card values.

| Rank | Hand | What it is | Example |
|---|---|---|---|
| 10 | **Royal Flush** | A→K→Q→J→10, all the same suit (the best possible hand) | A♠ K♠ Q♠ J♠ 10♠ |
| 9 | **Straight Flush** | Five cards in sequence, all the same suit | 9♥ 8♥ 7♥ 6♥ 5♥ |
| 8 | **Four of a Kind** | Four cards of the same rank | Q♠ Q♥ Q♦ Q♣ 4♠ |
| 7 | **Full House** | Three of a kind + a pair | K♠ K♥ K♦ 7♣ 7♠ |
| 6 | **Flush** | Five cards of the same suit, not in sequence | A♦ J♦ 8♦ 5♦ 2♦ |
| 5 | **Straight** | Five cards in sequence, mixed suits | 10♠ 9♥ 8♦ 7♣ 6♠ |
| 4 | **Three of a Kind** | Three cards of the same rank | 8♠ 8♥ 8♦ K♣ 2♠ |
| 3 | **Two Pair** | Two different pairs | J♠ J♥ 4♦ 4♣ 9♠ |
| 2 | **One Pair** | Two cards of the same rank | 10♠ 10♥ K♦ 6♣ 3♠ |
| 1 | **High Card** | None of the above — your single highest card plays | A♠ Q♥ 9♦ 5♣ 2♠ |

**Tie-breakers:** when two players share the same hand type, the higher-value cards decide it — e.g. a pair of Kings beats a pair of 7s; if the pairs are equal, the highest remaining "kicker" cards are compared. **Card value order (high → low):** A, K, Q, J, 10, 9, 8, 7, 6, 5, 4, 3, 2 (the Ace can also act as the low card in a 5-4-3-2-A straight).

Use this ranking to judge what a lot is worth to you: a card is valuable **only if it moves you toward a higher-ranked hand** (e.g. completing a flush or straight, pairing your hole cards, or upgrading three-of-a-kind into a full house).

---

## Auction Types

### Open Auction
An ascending-price bidding war. Players can bid as many times as they like, but each bid must be higher than the last. The timer resets with each new bid, so the tension builds. Last bidder standing wins.

### Silent Auction
Every player submits a single sealed bid simultaneously. No one knows what others are bidding. Highest bid wins — but you only get one shot.

### Dutch Auction
The price starts high and drops fast. The first player to hit the accept button wins at the current price. Risk waiting for a lower price, or grab it now before someone else does.

---

## Jokers

Between auction cycles, a **shop opens for 20 seconds** where players can spend credits on joker power-ups:

| Joker | Cost | Effect |
|---|---|---|
| **Sneak Peek** | 15 cr | Peek at one of a target player's hidden hole cards |
| **Bid Sweep** | 20 cr | Reject the current 3-card lot before bidding starts — force a fresh draw |
| **Block Bid** | 35 cr | Lock a target player out of bidding for one auction |
| **Love Letter** | 1 cr | Send a message to a target player (purely social) |

Each joker is single-use. Players can hold multiple jokers and choose when to deploy them.

---

## Player Economy

Every player receives **50 credits** at the start of each round, added on top of any credits carried over from previous rounds. Credits are spent bidding on card lots and buying jokers. Only the auction winner pays their bid — losing bidders keep their credits for the next cycle. This means a conservative player accumulates a larger budget over time, but a larger budget only translates into an advantage if it is eventually spent winning auctions that matter.

---

## Managing Your Chips — Be Smart With Credits

Your credits are a **fixed budget for the whole round, not for a single auction.** A round has *multiple* auction cycles, and each lot you win contributes cards to your final hand. This creates the core tension:

- **Spend everything to win one auction and you are broke for the rest of the round.** You may grab one great card, but you will be unable to bid on — let alone win — any later lot, and you can't buy jokers. One strong card rarely makes a winning 5-card hand on its own.
- **Hoard credits and win nothing, and you contribute no cards to the board** and have no influence over which community cards appear.
- **Finishing the round with unspent credits on key auctions is a strategic failure.** Credits do carry over between rounds, and you receive an additional 50 credits at the start of each new round — so saving chips gives you a larger budget later. However, a bigger budget only matters if you win the game, and you win the game by winning rounds, and you win rounds by building strong hands, and you build strong hands by winning the *right* auctions. Hoarding credits across rounds while consistently losing the auctions that would have improved your hand is a losing strategy — the extra chips become meaningless if you never convert them into board control.

**The governing principle: how much you spend on a lot should be directly proportional to how much that lot improves your hand** (using the Poker Hand Rankings above). A card that completes a flush, makes a straight, or pairs your hole cards is worth a large bid; a card that does nothing for your hand is worth little or nothing — let it go. Never let "winning the auction" become the goal in itself; the bid is only justified by the rank your hand gains.

So treat bidding as **budget allocation across the round, not a fight to win the current lot:**

1. **Score the lot against your hand first.** Estimate the hand rank you'd reach *with* the card vs. *without* it. The bigger that jump (e.g. High Card → Flush is huge; Pair → Two Pair is modest; no change is zero), the more credits the lot justifies. Bid in proportion to that gain.
2. **Know how many auction cycles likely remain** and roughly divide your remaining credits across them — don't blow your whole stack on the first lot.
3. **Bid the minimum needed to win**, not the maximum you can afford. In an open auction, raise in small increments; in a dutch auction, wait for the price to fall to your valuation rather than grabbing early.
4. **Reserve credits for jokers and late-round lots.** Keeping a small reserve lets you snipe a pivotal final card or deploy a joker (e.g. Block Bid) at a decisive moment.
5. **Walking away is a valid move.** Conceding a lot that doesn't raise your hand rank preserves credits and keeps you competitive in the auctions that actually decide the round.

**Bottom line:** winning the round correlates with winning the *right* auctions efficiently — the ones that raise your hand rank the most per credit — not with winning every auction. Pace your spending so you can still compete in the final, often most important, cycles.

---

## Bidding Intelligence — Read the Room

Your bid does not exist in isolation. To win efficiently you must consider **what opponents can still spend** and **how much they need the lot** — not just what the card is worth to your own hand.

### Track Opponent Balances

Every credit an opponent spends in a previous auction is a credit they cannot spend in this one. Before each auction, estimate how much each opponent has left:
- An opponent who has already won several auctions is likely running low. You may be able to outbid them cheaply.
- An opponent who has not bid on anything yet still has their full 50-credit budget and can outspend you if they choose to.
- If you are the only player who actually needs the current lot (e.g. a card that only completes *your* flush draw), you can bid modestly — no one will pay a high price for a card that does nothing for them. If multiple players are chasing the same hand type from the lot, expect a contested auction and budget accordingly.

### Card Selection Gives You Board Control

Remember: the auction winner does not have to take all three cards — they **choose which card(s) go to the community board** and return the rest to the deck. Winning an auction lets you:
- Put the card you need on the board.
- **Deny opponents a card they need** by choosing not to place it (it goes back to the deck, out of play).

When the lot contains a card that would significantly help a leading opponent, factor that denial value into your bid. Paying extra to stop someone from getting a flush-completing card can be worth more than the card is worth to your own hand.

### Silent Auction — One Bid, No Second Chances

The silent auction is the most demanding format because **your single sealed bid is final**. You cannot react to what others bid. This requires a different thought process before submitting:

1. **Decide your true valuation first.** Ask: what is the maximum I would be willing to pay for this lot before I'd rather let it go? That is your ceiling. Do not submit a number above it, but do not submit significantly below it either.
2. **Estimate opponent bids, not just opponent balances.** Think about whether your opponents *need* this lot. A card that only helps you is unlikely to attract high bids from others — you can win it for less. A card that helps everyone (e.g. a high-rank community card good for any hand) will attract competitive bids — you need to bid near your ceiling to have a real chance.
3. **Do not underbid on a must-have card to save chips.** If losing this auction means you have no path to a strong hand, bid what it takes to win. The chips you "save" by underbidding are worthless if you lose the lot and lose the round.
4. **Do not overbid on a nice-to-have card.** If the card offers a modest improvement and you do not need it to stay competitive, a mid-range bid is enough. Winning a low-value lot at full price cripples your budget for more important auctions later.
5. **Consider the number of remaining auction cycles and rounds.** Credits carry over and grow by 50 each round, so there is always a future to save for. But that future value is zero if you lose the current round by skipping a pivotal auction. If this lot is the decisive one for your hand, bid to win it — the credits you save by underbidding and losing are worth less than the round you throw away.

**Silent auction summary:** think of it as placing a bet, not opening a negotiation. You will not get a second chance. Commit to a number that reflects both the card's value to *your* hand and the likely competition from opponents — then do not second-guess it.
