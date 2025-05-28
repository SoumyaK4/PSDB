import os
import sqlite3
from sgfmill import sgf, boards, common  # ✅ fix: import common for BLACK/WHITE

DB_FILE = "pattern.db"
SGF_DIR = "sgf"
LOCAL_SIZE = 9

# ... (rotation, flipping, symmetry functions stay the same)

def get_local_pattern(board, x, y):
    half = LOCAL_SIZE // 2
    pattern = ""
    for dy in range(-half, half + 1):
        for dx in range(-half, half + 1):
            xx, yy = x + dx, y + dy
            if 0 <= xx < 19 and 0 <= yy < 19:
                stone = board.get(xx, yy)
                if stone == common.BLACK:   # ✅ use common.BLACK
                    pattern += 'B'
                elif stone == common.WHITE:  # ✅ use common.WHITE
                    pattern += 'W'
                else:
                    pattern += '.'
            else:
                pattern += 'X'
    return pattern

# ... rest of the code remains the same