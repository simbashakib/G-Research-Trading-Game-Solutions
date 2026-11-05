from backend.simulate import empirical_values


LEARNING_TURNS = 100
REFIT_EVERY = 100

history = []
V = []
last_fit = 0


def round_2(reward, lockout, t, T, your_score, other_scores, is_locked):
    global last_fit

    if t == 1:
        history.clear()
        V.clear()
        last_fit = 0

    history.append(reward)

    if is_locked or t <= LEARNING_TURNS:
        return False
    
    samples = history[:-1]
    remaining = T - t + 1

    if not V or len(samples) - last_fit >= REFIT_EVERY:
        V[:] = empirical_values(samples, remaining, lockout)
        last_fit = len(samples)

    A = V[remaining - 1]
    B = V[max(0, remaining - lockout - 1)]
    threshold = A - B

    return bool(reward > threshold)
