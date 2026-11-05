import numpy as np 
from scipy.special import lambertw

def round_1(reward, lockout, t, T, your_score, other_scores, is_locked):
    if is_locked:
        return False

    k = 10 * lambertw(15).real
    
    reward_per_turn = (k + 10) / ( np.exp(k / 10) + 15)

    if reward > reward_per_turn:
        return True


    return False 