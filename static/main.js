let board = new WGo.Board(document.getElementById("board"), {
  width: 400
});

let game = new WGo.Game(19);
let position = board.position;

board.addEventListener("click", function(x, y) {
    game.play(x, y);
    board.addObject({ x, y, c: game.turn === WGo.B ? WGo.W : WGo.B });
    let pattern = extractPattern(x, y);
    fetchPattern(pattern);
});

function extractPattern(cx, cy) {
    let size = 9;
    let half = Math.floor(size / 2);
    let str = "";
    for (let dy = -half; dy <= half; dy++) {
        for (let dx = -half; dx <= half; dx++) {
            let x = cx + dx, y = cy + dy;
            if (x < 0 || x >= 19 || y < 0 || y >= 19) {
                str += "X";
            } else {
                let stone = board.position.get(x, y);
                if (stone === WGo.B) str += "B";
                else if (stone === WGo.W) str += "W";
                else str += ".";
            }
        }
    }
    return str;
}

function getHeatColor(percent) {
    if (percent > 75) return "rgba(255,0,0,0.7)";
    if (percent > 50) return "rgba(255,165,0,0.6)";
    if (percent > 25) return "rgba(255,255,0,0.5)";
    if (percent > 10) return "rgba(0,255,0,0.4)";
    return "rgba(0,0,255,0.3)";
}

function fetchPattern(pattern) {
    fetch("/pattern", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pattern })
    })
    .then(res => res.json())
    .then(data => {
        board.removeAllObjects();
        data.sort((a, b) => b[1] - a[1]);
        let total = data.reduce((acc, curr) => acc + curr[1], 0);
        data.forEach(([move, count]) => {
            let [x, y] = move.replace(/[()]/g, "").split(",").map(Number);
            let percent = (count / total) * 100;
            board.addObject({ x, y, type: "stone", c: WGo.DIM, opacity: 0.4 });
            board.addObject({ x, y, type: "markup", text: percent.toFixed(0) + "%", color: getHeatColor(percent) });
        });
    });
}