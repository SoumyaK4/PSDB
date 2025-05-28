import os
import sqlite3
from sgfmill import sgf, boards

DB_FILE = "pattern.db"
SGF_DIR = "sgf"
LOCAL_SIZE = 9

def rotate90(pattern):
    size = LOCAL_SIZE
    matrix = [list(pattern[i*size:(i+1)*size]) for i in range(size)]
    return ''.join([''.join([matrix[size-j-1][i] for j in range(size)]) for i in range(size)])

def flip_horizontal(pattern):
    size = LOCAL_SIZE
    matrix = [pattern[i*size:(i+1)*size] for i in range(size)]
    return ''.join(row[::-1] for row in matrix)

def all_symmetries(pattern):
    patterns = [pattern]
    for _ in range(3):
        pattern = rotate90(pattern)
        patterns.append(pattern)
    flipped = [flip_horizontal(p) for p in patterns]
    patterns.extend(flipped)
    return patterns

def normalize_pattern(pattern):
    return min(all_symmetries(pattern))

def get_local_pattern(board, x, y):
    half = LOCAL_SIZE // 2
    pattern = ""
    for dy in range(-half, half + 1):
        for dx in range(-half, half + 1):
            xx, yy = x + dx, y + dy
            if 0 <= xx < 19 and 0 <= yy < 19:
                stone = board.get(xx, yy)
                if stone == boards.BLACK:
                    pattern += 'B'
                elif stone == boards.WHITE:
                    pattern += 'W'
                else:
                    pattern += '.'
            else:
                pattern += 'X'  # outside board
    return pattern

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS patterns (
            pattern TEXT,
            next_move TEXT,
            count INTEGER,
            PRIMARY KEY (pattern, next_move)
        )
    ''')
    c.execute("CREATE INDEX IF NOT EXISTS idx_pattern ON patterns(pattern)")
    conn.commit()
    return conn

def insert_pattern(conn, pattern, next_move):
    c = conn.cursor()
    c.execute('SELECT count FROM patterns WHERE pattern=? AND next_move=?', (pattern, next_move))
    row = c.fetchone()
    if row:
        c.execute('UPDATE patterns SET count = count + 1 WHERE pattern=? AND next_move=?', (pattern, next_move))
    else:
        c.execute('INSERT INTO patterns (pattern, next_move, count) VALUES (?, ?, 1)', (pattern, next_move))
    conn.commit()

def process_all_sgfs():
    conn = init_db()
    for filename in os.listdir(SGF_DIR):
        if not filename.endswith(".sgf"):
            continue
        with open(os.path.join(SGF_DIR, filename), "rb") as f:
            try:
                sgf_game = sgf.Sgf_game.from_bytes(f.read())
                board = boards.Board(19)
                main_sequence = sgf_game.get_main_sequence()

                for i in range(len(main_sequence)):
                    node = main_sequence[i]
                    move = node.get_move()
                    if move is None:
                        continue
                    color, (x, y) = move
                    if x is None or y is None:
                        continue

                    # Before playing the move, capture the pattern
                    pattern = normalize_pattern(get_local_pattern(board, x, y))

                    if i + 1 < len(main_sequence):
                        next_move = main_sequence[i + 1].get_move()[1]
                        if next_move:
                            insert_pattern(conn, pattern, str(next_move))

                    board.play(x, y, color)

            except Exception as e:
                print(f"Error in {filename}: {e}")
    conn.close()

if __name__ == "__main__":
    process_all_sgfs()