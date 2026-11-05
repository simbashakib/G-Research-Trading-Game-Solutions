import numpy as np

T = 2000
lockout = 15
mean = 10

V = [0.0] * (T + 1)

for n in range(1, T + 1):
    A = V[n - 1]
    B = V[max(0, n - lockout - 1)]

    threshold = A - B
    V[n] = A + mean * np.exp(-threshold / mean)


def round_1(reward, lockout, t, T, your_score, other_scores, is_locked):
    if is_locked:
        return False

    if reward > V[T - t] - V[max(0, T - t - lockout)]:
        return True


    return False 