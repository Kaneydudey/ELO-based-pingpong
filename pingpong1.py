PLAYERS = ["Kaako", "Kei", "Tai", "Misa", "Kane", "Mina"]

def init_stats(players):
    return {p: {"wins": 0, "losses": 0, "played": 0, "points": 0} for p in players} # p stands for player

def show_players(players):
    print("\nPlayer:")
    for i, p in enumerate(players, start=1):
        print(f"  {i}. {p}")

def pick_four(players):
    #Ask for four player numbers in one line and echo back (no validation yet).
    msg = "Choose FOUR player numbers separated by spaces (e.g. 1 2 3 4): "
    raw = input(msg).strip()
    print("You typed:", raw)
    return raw

def main():
    stats = init_stats(PLAYERS)
    show_players(PLAYERS)
    _raw = pick_four(PLAYERS)  # temporary; we’ll parse this next
    # The glue of the previous two functions
    
if __name__ == "__main__":
    main()

