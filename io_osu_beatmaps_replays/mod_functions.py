# mod_functions.py

from .constants import MOD_DOUBLE_TIME, MOD_HALF_TIME

def calculate_speed_multiplier(mods):
    speed_multiplier = 1.0
    if mods & MOD_DOUBLE_TIME:
        speed_multiplier = 1.5
    elif mods & MOD_HALF_TIME:
        speed_multiplier = 0.75
    return speed_multiplier
