"""Simulate trading decisions and estimate their average score."""

from dataclasses import dataclass
from bisect import bisect_right
import math
import random
import statistics
import time


class InvalidDecision(ValueError):
    """A strategy did not return True or False."""


@dataclass
class Result:
    score: float
    trade_turns: list[int]
    seconds: float


def empirical_values(samples, horizon, lockout):
    """Build V using the observed offers as equally likely future rewards."""
    ordered = sorted(samples)
    count = len(ordered)
    tail_sums = [0.0] * (count + 1)
    for i in range(count - 1, -1, -1):
        tail_sums[i] = tail_sums[i + 1] + ordered[i]

    values = [0.0] * (horizon + 1)
    for n in range(1, horizon + 1):
        A = values[n - 1]
        B = values[max(0, n - lockout - 1)]
        threshold = A - B

        # V(n) = A + average(max(0, x - threshold)).
        # Sorted offers and tail sums avoid scanning every sample for each n.
        i = bisect_right(ordered, threshold)
        excess = (tail_sums[i] - (count - i) * threshold) / count
        values[n] = A + max(0.0, excess)

    return values


def simulate(play, rewards: list[float], lockout: int = 15) -> Result:
    """Run one game. Accepting at turn t locks the next `lockout` turns."""
    if not rewards or any(not math.isfinite(reward) for reward in rewards):
        raise ValueError("rewards must be a nonempty list of finite numbers")
    if lockout < 0:
        raise ValueError("lockout must be nonnegative")
    score = 0.0
    locked_until = 0
    trades = []
    started = time.perf_counter()

    for t, reward in enumerate(rewards, start=1):
        is_locked = t <= locked_until
        accept = play(reward, lockout, t, len(rewards), score, is_locked)
        if not isinstance(accept, bool):
            raise InvalidDecision(
                f"Your strategy returned {accept!r} on turn {t}. "
                "Return True or False on every turn."
            )
        if accept and not is_locked:
            score += reward
            trades.append(t)
            locked_until = t + lockout

    return Result(score, trades, time.perf_counter() - started)


def generate_rewards(distribution: str, turns: int, mean: float, rng: random.Random) -> list[float]:
    """Draw independent rewards from a distribution with the given mean."""
    if distribution == "exponential":
        return [rng.expovariate(1 / mean) for _ in range(turns)]
    if distribution == "uniform":
        return [rng.uniform(0, 2 * mean) for _ in range(turns)]
    if distribution == "lognormal":
        return [rng.lognormvariate(math.log(mean) - 0.5, 1.0) for _ in range(turns)]
    if distribution == "mixture":
        # The weighted mean is 0.9 * (0.5 * mean) + 0.1 * (5.5 * mean).
        rewards = []
        for _ in range(turns):
            if rng.random() < 0.9:
                component_mean = 0.5 * mean
            else:
                component_mean = 5.5 * mean
            rewards.append(rng.expovariate(1 / component_mean))
        return rewards
    raise ValueError(f"unknown distribution: {distribution}")


def evaluate(
    function,
    games=100,
    turns=2000,
    lockout=15,
    distribution="exponential",
    mean=10.0,
    seed=42,
) -> list[Result]:
    """Simulate your function repeatedly, print its results, and return them."""
    if games < 1 or turns < 1:
        raise ValueError("games and turns must be positive")
    if not math.isfinite(mean) or mean <= 0:
        raise ValueError("mean must be finite and positive")
    if lockout < 0:
        raise ValueError("lockout must be nonnegative")

    results = []
    for game in range(games):
        rng = random.Random(seed + game)
        rewards = generate_rewards(distribution, turns, mean, rng)
        results.append(simulate(function, rewards, lockout))

    report(results, turns)
    return results


def report(results: list[Result], turns: int) -> None:
    scores = [result.score for result in results]
    trades = [len(result.trade_turns) for result in results]
    total_seconds = sum(result.seconds for result in results)
    milliseconds = 1000 * total_seconds / (len(results) * turns)

    print(f"Mean score: {statistics.mean(scores):.2f}")
    if len(scores) > 1:
        sd = statistics.stdev(scores)
        se = sd / math.sqrt(len(scores))
        print(f"SD: {sd:.2f}; SE: {se:.2f}")
    else:
        print("SD and SE need at least two games.")
    print(f"Mean trades: {statistics.mean(trades):.1f}")
    print(f"Time per turn: {milliseconds:.3f} ms")


def run_experiments(round_1, round_2, games=2000, round_2_distribution="mixture"):
    """Print results for each round, allowing either answer to be unfinished."""
    rounds = [
        ("Round 1", round_1, "exponential"),
        ("Round 2", round_2, round_2_distribution),
    ]
    for name, strategy, distribution in rounds:
        print(f"\n{name} — {games} games, {distribution} rewards")
        try:
            evaluate(strategy, games=games, distribution=distribution)
        except InvalidDecision as error:
            print(f"No result: {error}")


if __name__ == "__main__":
    import unittest

    class GameTests(unittest.TestCase):
        def test_empirical_values_against_all_small_game_choices(self):
            from functools import lru_cache

            samples = [-2.0, 1.0, 7.0]
            for lockout in (0, 1, 2, 15):
                @lru_cache(None)
                def optimal(n):
                    if n <= 0:
                        return 0.0
                    return sum(
                        max(optimal(n - 1), x + optimal(n - lockout - 1))
                        for x in samples
                    ) / len(samples)

                values = empirical_values(samples, 8, lockout)
                for n, value in enumerate(values):
                    self.assertAlmostEqual(value, optimal(n))

        def test_lockout_and_observations(self):
            calls = []

            def always(*args):
                calls.append(args)
                return True

            result = simulate(always, [1.0] * 34)
            self.assertEqual(result.trade_turns, [1, 17, 33])
            self.assertEqual(result.score, 3)
            self.assertEqual(len(calls), 34)
            self.assertTrue(all(args[5] for args in calls[1:16]))
            self.assertEqual(calls[16][4], 1.0)
            self.assertEqual(simulate(always, [1.0] * 4, 0).score, 4)

        def test_complete_games_and_reproducibility(self):
            def accept_positive(reward, lockout, t, T, your_score, is_locked):
                return not is_locked and reward > 0

            rewards = generate_rewards("mixture", 2000, 10, random.Random(42))
            self.assertEqual(rewards, generate_rewards("mixture", 2000, 10, random.Random(42)))
            first = simulate(accept_positive, rewards)
            second = simulate(accept_positive, rewards)
            self.assertEqual(first.score, second.score)
            self.assertEqual(first.trade_turns, second.trade_turns)
            self.assertTrue(all(b - a >= 16 for a, b in zip(first.trade_turns, first.trade_turns[1:])))

    unittest.main()
