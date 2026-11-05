from scipy.special import lambertw

def round_1(reward, lockout, t, T, your_score, other_scores, is_locked):
    if is_locked:
        return False

    k = 10 * lambertw(15).real

    if reward > k:
        return True


    return False 