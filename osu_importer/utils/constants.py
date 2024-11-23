# # osu_importer/utils/constants.py

SCALE_FACTOR = 0.01953125

# Mod constants for osu! Standard
MOD_NO_FAIL = 1 << 0               # No Fail
MOD_EASY = 1 << 1                  # Easy
MOD_TOUCH_DEVICE = 1 << 2          # Touch Device (optional, typically not used in standard)
MOD_HIDDEN = 1 << 3                # Hidden
MOD_HARD_ROCK = 1 << 4             # Hard Rock
MOD_SUDDEN_DEATH = 1 << 5          # Sudden Death
MOD_DOUBLE_TIME = 1 << 6           # Double Time
MOD_RELAX = 1 << 7                 # Relax (No key pressing, cursor only)
MOD_HALF_TIME = 1 << 8             # Half Time
MOD_NIGHTCORE = 1 << 9             # Nightcore (subset of Double Time, modifies pitch)
MOD_FLASHLIGHT = 1 << 10           # Flashlight
MOD_AUTO = 1 << 11                 # Auto (automatic gameplay)
MOD_SPUN_OUT = 1 << 12             # Spun Out (auto-completes spinners)
MOD_AUTOPILOT = 1 << 13            # Autopilot (cursor only, no key pressing)
MOD_PERFECT = 1 << 14              # Perfect (subset of Sudden Death, requires 100% accuracy)
MOD_CINEMA = 1 << 15               # Cinema (auto gameplay with focus on visuals)
MOD_SCORE_V2 = 1 << 30             # ScoreV2 (alternative scoring system)

MOD_FLAGS = {
    "No Fail": MOD_NO_FAIL,
    "Easy": MOD_EASY,
    "Hidden": MOD_HIDDEN,
    "Hard Rock": MOD_HARD_ROCK,
    "Sudden Death": MOD_SUDDEN_DEATH,
    "Double Time": MOD_DOUBLE_TIME,
    "Half Time": MOD_HALF_TIME,
    "Nightcore": MOD_NIGHTCORE,
    "Flashlight": MOD_FLASHLIGHT,
    "Perfect": MOD_PERFECT,
    "Spun Out": MOD_SPUN_OUT,
    "Autopilot": MOD_AUTOPILOT,
    "Relax": MOD_RELAX,
    "Cinema": MOD_CINEMA,
}

# Spinner center positions
SPINNER_CENTER_X = 256
SPINNER_CENTER_Y = 192
