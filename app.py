from flask import Flask, request, jsonify, render_template
import sqlite3

app = Flask(__name__)

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

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/pattern", methods=["POST"])
def search():
    data = request.json
    raw = data["pattern"]
    normalized = normalize_pattern(raw)
    conn = sqlite3.connect("pattern.db")
    c = conn.cursor()
    c.execute("SELECT next_move, count FROM patterns WHERE pattern=?", (normalized,))
    results = c.fetchall()
    conn.close()
    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)