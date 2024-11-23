# # osu_importer/utils/mod_functions.py

from osu_importer.utils.constants import MOD_DOUBLE_TIME, MOD_HALF_TIME

def calculate_speed_multiplier(mods):
    if mods & MOD_DOUBLE_TIME:
        return 1.5
    elif mods & MOD_HALF_TIME:
        return 0.75
    return 1.0
