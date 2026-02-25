const FILES = "abcdefgh";

const PIECE_TO_TEXT = {
  P: "♙",
  N: "♘",
  B: "♗",
  R: "♖",
  Q: "♕",
  K: "♔",
  p: "♟",
  n: "♞",
  b: "♝",
  r: "♜",
  q: "♛",
  k: "♚"
};

function parseFenBoard(fen) {
  const board = Array(64).fill(null);
  const [placement] = fen.split(" ");
  const ranks = placement.split("/");

  for (let rank = 0; rank < 8; rank += 1) {
    let file = 0;
    for (const char of ranks[rank]) {
      if (/\d/.test(char)) {
        file += Number(char);
      } else {
        const sq = (7 - rank) * 8 + file;
        board[sq] = char;
        file += 1;
      }
    }
  }

  return board;
}

function squareToCoords(square, size) {
  const file = square.charCodeAt(0) - 97;
  const rank = Number(square[1]) - 1;
  const cell = size / 8;
  return {
    x: file * cell + cell / 2,
    y: (7 - rank) * cell + cell / 2
  };
}

export default function ChessBoard({ fen, arrows = [] }) {
  const board = parseFenBoard(fen);
  const size = 560;
  const cell = size / 8;

  return (
    <svg className="board" viewBox={`0 0 ${size} ${size}`} role="img" aria-label="Chess board">
      <defs>
        <linearGradient id="lightSquare" x1="0" x2="1">
          <stop offset="0%" stopColor="#f8f2de" />
          <stop offset="100%" stopColor="#ecd9ad" />
        </linearGradient>
        <linearGradient id="darkSquare" x1="0" x2="1">
          <stop offset="0%" stopColor="#345a4f" />
          <stop offset="100%" stopColor="#213c35" />
        </linearGradient>
        <marker id="arrowHead" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
          <polygon points="0 0, 6 3, 0 6" fill="#ff8243" />
        </marker>
      </defs>

      {Array.from({ length: 64 }).map((_, index) => {
        const file = index % 8;
        const rank = 7 - Math.floor(index / 8);
        const isLight = (file + rank) % 2 === 0;
        return (
          <rect
            key={index}
            x={file * cell}
            y={Math.floor(index / 8) * cell}
            width={cell}
            height={cell}
            fill={isLight ? "url(#lightSquare)" : "url(#darkSquare)"}
          />
        );
      })}

      {arrows.map((arrow, idx) => {
        const from = squareToCoords(arrow.from, size);
        const to = squareToCoords(arrow.to, size);
        return (
          <line
            key={`${arrow.from}-${arrow.to}-${idx}`}
            x1={from.x}
            y1={from.y}
            x2={to.x}
            y2={to.y}
            stroke="#ff8243"
            strokeWidth="8"
            strokeLinecap="round"
            markerEnd="url(#arrowHead)"
            opacity="0.85"
          />
        );
      })}

      {board.map((piece, index) => {
        if (!piece) return null;
        const file = index % 8;
        const rank = Math.floor(index / 8);
        return (
          <text
            key={`${piece}-${index}`}
            x={file * cell + cell / 2}
            y={rank * cell + cell / 2 + 20}
            textAnchor="middle"
            fontSize="54"
            className="piece"
          >
            {PIECE_TO_TEXT[piece]}
          </text>
        );
      })}

      {FILES.split("").map((file, idx) => (
        <text key={file} x={idx * cell + 8} y={size - 8} className="coord">
          {file}
        </text>
      ))}

      {Array.from({ length: 8 }).map((_, idx) => (
        <text key={idx} x={6} y={idx * cell + 18} className="coord">
          {8 - idx}
        </text>
      ))}
    </svg>
  );
}
