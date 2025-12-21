
from secrets import choice
from turtle import mode


MIN_PLAYERS = 4
MAX_PLAYERS = 8

def ask_yes_no(prompt: str) -> bool:
    """Return True for 'y', False for 'n' (keeps asking otherwise)."""
    while True:
        ans = input(prompt).strip().lower()
        if ans in ("y", "n"):
            return ans == "y"
        print("Please enter y or n.")
def collect_players(min_n=MIN_PLAYERS, max_n=MAX_PLAYERS):
    """
    Ask for player names:
      - require at least min_n (default 4)
      - allow adding up to max_n (default 8)
      - prevent empty/duplicate names (case-insensitive)
    Returns a list of names in the *entered* order.
    """
    players = []
    def name_taken(name):  # case-insensitive duplicate check
        low = name.strip().lower()
        return any(low == p.lower() for p in players)

    # required first 4
    while len(players) < min_n:
        n = len(players) + 1
        name = input(f"add player {n}: ").strip()
        if not name:
            print("Name cannot be empty.")
            continue
        if name_taken(name):
            print("That name is already added.")
            continue
        players.append(name)

    # optional extra players up to max
    while len(players) < max_n and ask_yes_no("add new player? (y/n): "):
        n = len(players) + 1
        name = input(f"add player {n}: ").strip()
        if not name:
            print("Name cannot be empty.")
            continue
        if name_taken(name):
            print("That name is already added.")
            continue
        players.append(name)

    return players
def init_stats(players):
    return {
        p: {"wins": 0, "losses": 0, "played": 0, "points": 0, "pf": 0, "pa": 0}
        for p in players
    }
 # p stands for player

def show_players(players):
    print("\nPlayer:")
    for i, p in enumerate(players, start=1):
        print(f"  {i}. {p}")

def pick_four(players):
    """Ask for four distinct player numbers; keep asking until valid.
       Returns a list of 0-based indices, e.g. [0,1,2,3].
    """
    N = len(players)
    while True:
        msg = f"Choose FOUR player numbers separated by spaces (1..{N}, e.g. 1 2 3 4): "
        raw = input(msg).strip()
        raw = raw.replace(",", " ")           # allow commas or spaces
        parts = raw.split()

        # 1) exactly four items?
        if len(parts) != 4:
            print("Please enter exactly FOUR numbers.")
            continue

        # 2) all digits?
        if not all(x.isdigit() for x in parts):
            print("Please enter numbers only.")
            continue

        nums = [int(x) for x in parts]

        # 3) in range?
        if not all(1 <= n <= N for n in nums):
            print(f"Numbers must be between 1 and {N}.")
            continue

        # 4) all unique?
        if len(set(nums)) != 4:
            print("Duplicate numbers detected — pick four different players.")
            continue

        # convert to 0-based indices and return
        return [n - 1 for n in nums]  

# --- Fairness state helpers ---
def pair_key(a, b):
    """Unordered key for a 2-player pair (so ('Kei','Kaako') == ('Kaako','Kei'))."""
    return tuple(sorted((a, b)))
def init_fairness(players):
    """Create counters the scheduler will use later."""
    return {
        "partner": {},                     # (A,B) -> times they partnered
        "opponent": {},                    # (A,B) -> times they faced each other
        "rest": {p: 0 for p in players},   # A -> times A rested
    }
def _bump(d, key, by=1):
    """Increment a dict counter safely."""
    d[key] = d.get(key, 0) + by
def update_fairness(fair, team1, team2, resting):
    """Update partner/opponent/rest counters after a match."""
    a, b = team1
    c, d = team2

    # partners (unordered)
    _bump(fair["partner"], pair_key(a, b))
    _bump(fair["partner"], pair_key(c, d))

    # opponents (unordered): each cross pairing between teams
    for x in team1:
        for y in team2:
            _bump(fair["opponent"], pair_key(x, y))

    # rests
    for p in resting:
        fair["rest"][p] = fair["rest"].get(p, 0) + 1
# (Optional) quick peek printer while you test
def debug_fairness(fair):
    p_used = {f"{a}+{b}": n for (a, b), n in fair["partner"].items()}
    print("partners used:", p_used)
    print("rests:", fair["rest"])


def prompt_winner():
    """Return 1 or 2 after validating input."""
    while True:
        w = input("Who won? (1 or 2): ").strip()
        if w in ("1", "2"):
            return int(w)
        print("Please type 1 or 2.")
def prompt_scores(team1, team2, winner_team):
    """Return (s1, s2) for team1 vs team2 after validating your rules."""
    label1 = f"{team1[0]}+{team1[1]}"
    label2 = f"{team2[0]}+{team2[1]}"

    while True:
        raw = input(f"Enter score for Team1 ({label1}) and Team2 ({label2}) e.g. 11-7: ").strip()
        # allow "11-7", "11 7", "11,7", "11:7"
        for ch in ",-:":
            raw = raw.replace(ch, " ")
        parts = [p for p in raw.split() if p]

        if len(parts) != 2 or not all(p.isdigit() for p in parts):
            print("Please enter two numbers like 11-7.")
            continue

        s1, s2 = map(int, parts)
        if s1 > 12 or s2 > 12:
            print("Scores must be ≤ 12.")
            continue

        # winner alignment
        if winner_team == 1 and not (s1 > s2):
            print("Team 1 was marked the winner, so its score must be higher.")
            continue
        if winner_team == 2 and not (s2 > s1):
            print("Team 2 was marked the winner, so its score must be higher.")
            continue

        # validity of the winning score
        hi, lo = (s1, s2) if s1 > s2 else (s2, s1)
        if hi == 11:
            if lo > 9:
                print("At 11 the margin must be ≥2 (e.g., 11–9).")
                continue
        elif hi == 12:
            if lo not in (10, 11):
                print("At 12 the other side must be 10 or 11.")
                continue
        else:
            print("Winning score must be 11 or 12.")
            continue

        return s1, s2
    
def confirm_result(team1, team2, winner, s1, s2):
    t1 = f"{team1[0]}+{team1[1]}"
    t2 = f"{team2[0]}+{team2[1]}"
    print(f"\nConfirm result:  {t1}  {s1}-{s2}  {t2}   (winner: team {winner})")
    return ask_yes_no("Is this correct? (y/n): ")
def apply_result(stats, team1, team2, winner_team, s1, s2):
    winners = team1 if winner_team == 1 else team2
    losers  = team2 if winner_team == 1 else team1

    win_score = s1 if winner_team == 1 else s2
    lose_score = s2 if winner_team == 1 else s1

    for p in winners:
        stats[p]["wins"]   += 1
        stats[p]["played"] += 1
        stats[p]["points"] += 1          # v1: 1 point per win
        stats[p]["pf"]     += win_score
        stats[p]["pa"]     += lose_score

    for p in losers:
        stats[p]["losses"] += 1
        stats[p]["played"] += 1
        stats[p]["pf"]     += lose_score
        stats[p]["pa"]     += win_score
def show_leaderboard(stats):
    print("\nLeaderboard")
    rows = sorted(
        stats.items(),
        key=lambda kv: (-kv[1]["points"], -kv[1]["wins"], kv[1]["losses"], kv[0]),
    )
    for name, s in rows:
        gp = s["played"]
        pf = s["pf"]; pa = s["pa"]
        pf_avg = (pf / gp) if gp else 0.0
        pa_avg = (pa / gp) if gp else 0.0
        print(
            f"{name:12}  Pts:{s['points']:2d}  W:{s['wins']:2d}  L:{s['losses']:2d}  "
            f"GP:{gp:2d}  PF:{pf:3d}  PA:{pa:3d}  PF/G:{pf_avg:4.1f}  PA/G:{pa_avg:4.1f}"
        )

# --- Candidate generation (no imports) ---
def generate_candidates(players):
    """
    Yield all possible matches as (team1, team2, resting),
    where team1/team2 are tuples of player names.
    For any 4 picked players there are 3 unique 2v2 splits:
    (0,1 vs 2,3), (0,2 vs 1,3), (0,3 vs 1,2).
    """
    n = len(players)
    cands = []
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                for l in range(k + 1, n):
                    quad = [players[i], players[j], players[k], players[l]]
                    a, b, c, d = quad
                    resting = [p for p in players if p not in quad]
                    cands.append(((a, b), (c, d), resting))
                    cands.append(((a, c), (b, d), resting))
                    cands.append(((a, d), (b, c), resting))
    return cands

# --- Heuristic scoring ---

W_PARTNER = 10   # penalize repeated partners strongly
W_OPP     = 3    # penalize repeated opponents
W_SPREAD  = 2    # penalize uneven 'played' among the 4
W_REST    = 1    # penalize resting players who already rested a lot

def score_candidate(team1, team2, resting, fair, stats):
    """
    Higher score = better (fresher partners/opponents, balanced play/rest).
    """
    # partner repeats
    p1 = fair["partner"].get(pair_key(*team1), 0)
    p2 = fair["partner"].get(pair_key(*team2), 0)
    score = 0
    score -= W_PARTNER * (p1 + p2)

    # opponent repeats (all cross pairings)
    opp = 0
    for x in team1:
        for y in team2:
            opp += fair["opponent"].get(pair_key(x, y), 0)
    score -= W_OPP * opp

    # balance: prefer sets of four who have played a similar amount
    plays = [stats[p]["played"] for p in (team1[0], team1[1], team2[0], team2[1])]
    spread = max(plays) - min(plays)
    score -= W_SPREAD * spread

    # rest fairness: avoid resting people who already rested a lot
    rest_pen = sum(fair["rest"].get(p, 0) for p in resting)
    score -= W_REST * rest_pen

    return score
def suggest_next_indices(players, fair, stats):
    """
    Choose the highest-scoring candidate and return four indices
    in the order [team1_a, team1_b, team2_a, team2_b].
    """
    best = None
    best_score = float("-inf")
    for team1, team2, resting in generate_candidates(players):
        s = score_candidate(team1, team2, resting, fair, stats)
        if s > best_score:
            best_score = s
            best = (team1, team2)

    # convert chosen teams (names) back to indices
    (a, b), (c, d) = best
    idxs = [players.index(a), players.index(b), players.index(c), players.index(d)]
    return idxs

# --- Match history helpers ---

def record_match(matches, round_no, team1, team2, winner, s1, s2, resting):
    """Append one match to history."""
    matches.append({
        "round": round_no,
        "team1": tuple(team1),
        "team2": tuple(team2),
        "winner": winner,          # 1 or 2
        "score": (s1, s2),         # (team1, team2)
        "resting": tuple(resting),
    })
def print_recap(matches):
    """Pretty-print all recorded matches so far."""
    if not matches:
        print("\nNo matches recorded yet.")
        return
    print("\n=== Match Recap ===")
    for m in matches:
        t1 = f"{m['team1'][0]}+{m['team1'][1]}"
        t2 = f"{m['team2'][0]}+{m['team2'][1]}"
        s1, s2 = m["score"]
        star1 = "★" if m["winner"] == 1 else " "
        star2 = "★" if m["winner"] == 2 else " "
        rest = ", ".join(m["resting"])
        # R01  ★  Kei+Mina   12-10  Tai+Misa           rest: Kaako, Kane
        print(f"R{m['round']:02d}  {star1} {t1:12} {s1:>2}-{s2:<2} {t2:12} {star2}  rest: {rest}")


def main():
    players = collect_players()          # <- interactive list
    stats = init_stats(players)
    fair = init_fairness(players)

    matches = []        
    round_no = 1

    while True:
        show_players(players)

        # idxs = pick_four(players)                    # old manual-only
        mode = input("\nNext match: (a)uto or (m)anual? ").strip().lower()
        if mode == "m":
            idxs = pick_four(players)
        else:
            idxs = suggest_next_indices(players, fair, stats)
        # everything else already accepts 'players'
        team1 = (players[idxs[0]], players[idxs[1]])
        team2 = (players[idxs[2]], players[idxs[3]])
        resting = [name for i, name in enumerate(players) if i not in idxs]

        print(f"\nMatch: {team1[0]} + {team1[1]}  vs  {team2[0]} + {team2[1]}")
        print("Resting:", ", ".join(resting))

        # get a result, but confirm before saving
        while True:
            winner = prompt_winner()
            s1, s2 = prompt_scores(team1, team2, winner)
            if confirm_result(team1, team2, winner, s1, s2):
                break
            print("Okay, let's re-enter winner and scores...")

        apply_result(stats, team1, team2, winner, s1, s2)


        update_fairness(fair, team1, team2, resting)
        record_match(matches, round_no, team1, team2, winner, s1, s2, resting)
        show_leaderboard(stats)

        # ask what to do next (re-ask if user types 'r')
        while True:
            choice = input("\nPlay another? (y/n)  |  r = recap: ").strip().lower()
            if choice == "r":
                print_recap(matches)
                continue          # stay in this prompt loop
            if choice in ("y", "n"):
                break             # valid answer; leave this prompt loop
            print("Please type y, n, or r.")

        if choice != "y":
            print("\n=== Final Leaderboard ===")
            show_leaderboard(stats)
            print_recap(matches)
            print("みんな、頑張ったね!")
            return

        round_no += 1


if __name__ == "__main__":
    main()

