PLAYERS = ["Kaako", "Kei", "Tai", "Misa", "Kane", "Mina"]

def init_stats(players):
    return {p: {"wins": 0, "losses": 0, "played": 0, "points": 0} for p in players} # p stands for player

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
    
def prompt_winner():
    """Return 1 or 2 after validating input."""
    while True:
        w = input("Who won? (1 or 2): ").strip()
        if w in ("1", "2"):
            return int(w)
        print("Please type 1 or 2.")

def apply_result(stats, team1, team2, winner_team):
    """Update wins/losses/played/points for the four players."""
    winners = team1 if winner_team == 1 else team2
    losers  = team2 if winner_team == 1 else team1

    for p in winners:
        stats[p]["wins"]   += 1
        stats[p]["played"] += 1
        stats[p]["points"] += 1   # v1: 1 point per win
    for p in losers:
        stats[p]["losses"] += 1
        stats[p]["played"] += 1

def show_leaderboard(stats):
    print("\nLeaderboard")
    rows = sorted(
        stats.items(),
        key=lambda kv: (-kv[1]["points"], -kv[1]["wins"], kv[1]["losses"], kv[0])
    )
    for name, s in rows:
        print(f"{name:12}  Pts:{s['points']:2d}  W:{s['wins']:2d}  L:{s['losses']:2d}  GP:{s['played']:2d}")


def main():
    stats = init_stats(PLAYERS)
    show_players(PLAYERS)

    idxs = pick_four(PLAYERS)              # e.g. [0,1,2,3]
    team1 = (PLAYERS[idxs[0]], PLAYERS[idxs[1]])
    team2 = (PLAYERS[idxs[2]], PLAYERS[idxs[3]])
    resting = [name for i, name in enumerate(PLAYERS) if i not in idxs]

    print(f"\nMatch: {team1[0]} + {team1[1]}  vs  {team2[0]} + {team2[1]}")
    print("Resting:", ", ".join(resting))

    winner = prompt_winner()
    apply_result(stats, team1, team2, winner)
    show_leaderboard(stats)


    
if __name__ == "__main__":
    main()

