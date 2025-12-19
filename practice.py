PLAYERS = ["kaako", "Kei", "Tai", "Misa", "Kane", "Mina"]

def init_stats(players):
    return {p: {"wins": 0, "losses": 0, "played": 0, "points": 0} for p in players}

def show_players(players):
    print("\nPlayer:")
    for i, p in enumerate(players, start=1):
        print(f"  {i}. {p}")

