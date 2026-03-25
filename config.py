import numpy as np

# ----------------------------
# Audio settings
# ----------------------------
FS = 48000
BLOCK = 256
MASTER_GAIN = 0.2

ATTACK_SEC = 0.01
RELEASE_SEC = 0.08
ATTACK_STEP = 1.0 / max(1, int(ATTACK_SEC * FS / BLOCK))
RELEASE_STEP = 1.0 / max(1, int(RELEASE_SEC * FS / BLOCK))
