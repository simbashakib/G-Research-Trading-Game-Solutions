from round_1 import round_1
from round_2 import round_2
from simulate import run_experiments


if __name__ == "__main__":
    games = 2000
    run_experiments(round_1, round_2, games=games)