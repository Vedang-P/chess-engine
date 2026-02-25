import { FILES, indexToSquare, parseFenBoard } from "../lib/chess";

function displaySquareToBoardIndex(displayIndex, orientation) {
  const row = Math.floor(displayIndex / 8);
  const col = displayIndex % 8;

  if (orientation === "black") {
    const file = 7 - col;
    const rank = row;
    return rank * 8 + file;
  }

  const file = col;
  const rank = 7 - row;
  return rank * 8 + file;
}

function squareToDisplayCoords(square, size, orientation) {
  const file = square.charCodeAt(0) - 97;
  const rank = Number(square[1]) - 1;
  const cell = size / 8;

  const displayCol = orientation === "black" ? 7 - file : file;
  const displayRow = orientation === "black" ? rank : 7 - rank;

  return {
    x: displayCol * cell + cell / 2,
    y: displayRow * cell + cell / 2
  };
}

function heatOpacity(value) {
  return Math.min(0.26, 0.05 + Math.abs(value) * 0.03);
}

function pieceAssetName(piece) {
  const isWhite = piece === piece.toUpperCase();
  return `${isWhite ? "w" : "b"}${piece.toUpperCase()}`;
}

export default function ChessBoard({
  fen,
  orientation = "white",
  selectedSquare = null,
  legalTargets = [],
  lastMove = null,
  currentMove = "",
  hoveredSquare = null,
  heatmap = {},
  arrows = [],
  onSquareClick,
  onSquareHover
}) {
  const board = parseFenBoard(fen);
  const size = 640;
  const cell = size / 8;
  const legalTargetsSet = new Set(legalTargets);

  const currentFrom = currentMove?.slice(0, 2) || null;
  const currentTo = currentMove?.slice(2, 4) || null;

  return (
    <svg className="board" viewBox={`0 0 ${size} ${size}`} role="img" aria-label="Chess board">
      <defs>
        <linearGradient id="lightSquare" x1="0" x2="0" y1="0" y2="1">
          <stop offset="0%" stopColor="#f0d9b5" />
          <stop offset="100%" stopColor="#f0d9b5" />
        </linearGradient>
        <linearGradient id="darkSquare" x1="0" x2="0" y1="0" y2="1">
          <stop offset="0%" stopColor="#b58863" />
          <stop offset="100%" stopColor="#b58863" />
        </linearGradient>
        <marker id="arrowHead" markerWidth="10" markerHeight="10" refX="8" refY="3.5" orient="auto">
          <polygon points="0 0, 8 3.5, 0 7" fill="#7fa650" />
        </marker>
      </defs>

      {Array.from({ length: 64 }).map((_, displayIndex) => {
        const boardIndex = displaySquareToBoardIndex(displayIndex, orientation);
        const square = indexToSquare(boardIndex);
        const x = (displayIndex % 8) * cell;
        const y = Math.floor(displayIndex / 8) * cell;
        const file = boardIndex % 8;
        const rank = Math.floor(boardIndex / 8);
        const isLight = (file + rank) % 2 === 0;

        const isSelected = selectedSquare === square;
        const isTarget = legalTargetsSet.has(square);
        const isLastMove = lastMove && (lastMove.from === square || lastMove.to === square);
        const isCurrentMove = square === currentFrom || square === currentTo;
        const isHovered = hoveredSquare === square;
        const heat = heatmap[square] || 0;
        const heatPositive = heat > 0;

        return (
          <g
            key={square}
            onClick={() => onSquareClick?.(square)}
            onMouseEnter={() => onSquareHover?.(square)}
            onMouseLeave={() => onSquareHover?.(null)}
            style={{ cursor: "pointer" }}
          >
            <rect x={x} y={y} width={cell} height={cell} fill={isLight ? "url(#lightSquare)" : "url(#darkSquare)"} />

            {heat !== 0 && (
              <rect
                x={x + 1.5}
                y={y + 1.5}
                width={cell - 3}
                height={cell - 3}
                fill={heatPositive ? "#7fa650" : "#8f8a84"}
                opacity={heatOpacity(heat)}
              />
            )}

            {isLastMove && (
              <rect
                x={x + 2}
                y={y + 2}
                width={cell - 4}
                height={cell - 4}
                fill="none"
                stroke="#cdd26a"
                strokeWidth="3.5"
                opacity="0.92"
              />
            )}

            {isCurrentMove && (
              <rect
                x={x + 5}
                y={y + 5}
                width={cell - 10}
                height={cell - 10}
                fill="none"
                stroke="#6f9d4f"
                strokeWidth="4"
                opacity="0.95"
              />
            )}

            {isSelected && (
              <rect
                x={x + 4}
                y={y + 4}
                width={cell - 8}
                height={cell - 8}
                fill="none"
                stroke="#7fa650"
                strokeWidth="4"
              />
            )}

            {isTarget && (
              <circle cx={x + cell / 2} cy={y + cell / 2} r={cell * 0.14} fill="#6f9d4f" opacity="0.9" />
            )}

            {isHovered && (
              <rect
                x={x + 8}
                y={y + 8}
                width={cell - 16}
                height={cell - 16}
                fill="none"
                stroke="#6b6760"
                strokeWidth="2"
                opacity="0.72"
              />
            )}
          </g>
        );
      })}

      {arrows.map((arrow, idx) => {
        const from = squareToDisplayCoords(arrow.from, size, orientation);
        const to = squareToDisplayCoords(arrow.to, size, orientation);
        return (
          <line
            key={`${arrow.from}-${arrow.to}-${idx}`}
            x1={from.x}
            y1={from.y}
            x2={to.x}
            y2={to.y}
            stroke={arrow.color || "#7fa650"}
            strokeWidth={arrow.width || 8}
            strokeLinecap="round"
            markerEnd="url(#arrowHead)"
            opacity={arrow.opacity || 0.84}
          />
        );
      })}

      {Array.from({ length: 64 }).map((_, displayIndex) => {
        const boardIndex = displaySquareToBoardIndex(displayIndex, orientation);
        const piece = board[boardIndex];
        if (!piece) return null;

        const x = (displayIndex % 8) * cell;
        const y = Math.floor(displayIndex / 8) * cell;
        const asset = pieceAssetName(piece);

        return (
          <image
            key={`piece-${boardIndex}`}
            x={x + 4}
            y={y + 4}
            width={cell - 8}
            height={cell - 8}
            href={`/pieces/cburnett/${asset}.svg`}
            preserveAspectRatio="xMidYMid meet"
            pointerEvents="none"
          />
        );
      })}

      {(orientation === "white" ? FILES : FILES.split("").reverse().join("")).split("").map((file, idx) => (
        <text key={`file-${file}`} x={idx * cell + 8} y={size - 8} className="coord">
          {file}
        </text>
      ))}

      {Array.from({ length: 8 }).map((_, idx) => {
        const rankLabel = orientation === "white" ? 8 - idx : idx + 1;
        return (
          <text key={`rank-${rankLabel}`} x={7} y={idx * cell + 20} className="coord">
            {rankLabel}
          </text>
        );
      })}
    </svg>
  );
}
