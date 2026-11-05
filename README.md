# G-Research Trading Game Solutions

## Files

- `round_1.py`: write your Round 1 decision.
- `round_2.py`: write your Round 2 decision.
- `experiment.py`: click Run to see both strategies' results.
- `simulate.py`: all the backend machinery and its checks. You can ignore this file.

VS Code uses this project's `.venv` environment, which has NumPy and SciPy installed. Keep the interpreter set to `.venv` when running experiments.

To set up a fresh checkout, run `python3 -m venv .venv`, then `.venv/bin/python -m pip install -r requirements.txt`, and select `.venv/bin/python` as the interpreter in VS Code.

## Write an answer and run it

Each strategy receives the current offer and returns `True` to accept or `False` to skip. Complete your decision underneath the existing lockout check. Every path through your function must return a boolean.

Save your answer, open `experiment.py`, and click Run. Alternatively, run `.venv/bin/python experiment.py` in the terminal. It runs 2,000 games per round; change `games` in that file if you want a different number.

An unfinished answer gets a message explaining that it needs to return `True` or `False`. It gets no score, and the other round can still run.

## Inputs to your strategy

| Input | Meaning |
| --- | --- |
| `reward` | The offer available now. |
| `lockout` | Number of turns blocked after accepting (15). |
| `t` | Current turn, starting at 1. |
| `T` | Total number of turns (2,000). |
| `your_score` | Sum of accepted rewards so far. |
| `other_scores` | Empty in this solo simulator. |
| `is_locked` | Whether you are currently unable to trade. |

You do not need to use every input. If you add memory to your strategy, reset it at `t == 1` so each game starts fresh.

## Game rules

Rewards are independent draws. Accepting adds the full reward to your score and prevents trading for the next 15 turns. Accept on turn 1 and you can next trade on turn 17. Your function sees offers during lockout but cannot accept them.

Round 1 uses exponential rewards with mean 10 (rate 0.1). Round 2 uses a fixed distribution that your strategy is not told. The experiment uses a mixture distribution for Round 2 by default. You can pass `round_2_distribution` to `run_experiments`, choosing `exponential`, `uniform`, `lognormal`, or `mixture`; all have mean 10. Performance depends on this choice.

This is a local recreation of the solo rules, not the official server. There are no competitors or shared rewards.

## Results

- **Mean score** estimates the expected total reward per game.
- **SD** measures how much individual game scores vary.
- **SE** measures uncertainty in the estimated mean.
- **Mean trades** is the average number of accepted offers per game.
- **Time per turn** measures simulation speed.

The mean is a simulation estimate, not an exact expected value. A fixed seed makes scores reproducible.

## Backend checks

The checks live inside `simulate.py` and run only when that file is executed directly with `python3 simulate.py`. They do not run during your experiments. For normal use, just run `experiment.py`.
