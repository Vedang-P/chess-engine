import { useEffect, useState } from "react";

import { FILES, indexToSquare, parseFenBoard, squareToIndex } from "../lib/chess";

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

function pointerEventToSquare(event, size, orientation) {
  const svg = event.currentTarget;
  const rect = svg.getBoundingClientRect();
  if (rect.width <= 0 || rect.height <= 0) return null;

  const localX = ((event.clientX - rect.left) * size) / rect.width;
  const localY = ((event.clientY - rect.top) * size) / rect.height;
  if (localX < 0 || localY < 0 || localX >= size || localY >= size) return null;

  const col = Math.floor(localX / (size / 8));
  const row = Math.floor(localY / (size / 8));
  const displayIndex = row * 8 + col;
  const boardIndex = displaySquareToBoardIndex(displayIndex, orientation);
  return indexToSquare(boardIndex);
}

function pointerEventToCoords(event, size) {
  const svg = event.currentTarget;
  const rect = svg.getBoundingClientRect();
  if (rect.width <= 0 || rect.height <= 0) return null;

  const localX = ((event.clientX - rect.left) * size) / rect.width;
  const localY = ((event.clientY - rect.top) * size) / rect.height;
  const x = Math.max(0, Math.min(size, localX));
  const y = Math.max(0, Math.min(size, localY));
  return { x, y };
}

function heatOpacity(value) {
  return Math.min(0.7, 0.2 + Math.abs(value) * 0.07);
}

function heatColor(value) {
  const magnitude = Math.min(8, Math.abs(value));
  const t = magnitude / 8;

  if (value >= 0) {
    // Warm bright reds for increasing attacking pressure.
    const hue = Math.round(14 - t * 8);
    const sat = Math.round(76 + t * 18);
    const light = Math.round(44 + t * 16);
    return `hsl(${hue} ${sat}% ${light}%)`;
  }

  // Darker crimson shades for opposite pressure.
  const hue = Math.round(358 - t * 2);
  const sat = Math.round(62 + t * 18);
  const light = Math.round(22 + t * 14);
  return `hsl(${hue} ${sat}% ${light}%)`;
}

function pieceAssetName(piece) {
  const isWhite = piece === piece.toUpperCase();
  return `${isWhite ? "w" : "b"}${piece.toUpperCase()}`;
}

function arrowGeometry(from, to, cell) {
  const dx = to.x - from.x;
  const dy = to.y - from.y;
  const len = Math.hypot(dx, dy);
  if (len < 1e-6) return null;

  const ux = dx / len;
  const uy = dy / len;
  const px = -uy;
  const py = ux;

  const tailInset = cell * 0.18;
  const headLength = cell * 0.24;
  const headWidth = cell * 0.19;
  const tipInset = cell * 0.16;

  const sx = from.x + ux * tailInset;
  const sy = from.y + uy * tailInset;
  const tipX = to.x - ux * tipInset;
  const tipY = to.y - uy * tipInset;
  const ex = tipX - ux * headLength;
  const ey = tipY - uy * headLength;

  const leftX = ex + px * (headWidth / 2);
  const leftY = ey + py * (headWidth / 2);
  const rightX = ex - px * (headWidth / 2);
  const rightY = ey - py * (headWidth / 2);

  return {
    sx,
    sy,
    ex,
    ey,
    tipX,
    tipY,
    leftX,
    leftY,
    rightX,
    rightY
  };
}

export default function ChessBoard({
  fen,
  orientation = "white",
  selectedSquare = null,
  trackedSquare = null,
  legalTargets = [],
  lastMove = null,
  currentMove = "",
  hoveredSquare = null,
  dragFromSquare = null,
  dragToSquare = null,
  heatmap = {},
  arrows = [],
  onSquareHover,
  onSquareDown,
  onSquareUp,
  onSquareEnter,
  onSquareTap
}) {
  const board = parseFenBoard(fen);
  const size = 640;
  const cell = size / 8;
  const legalTargetsSet = new Set(legalTargets);
  const [dragPointer, setDragPointer] = useState(null);

  const currentFrom = currentMove?.slice(0, 2) || null;
  const currentTo = currentMove?.slice(2, 4) || null;
  const draggedPiece = dragFromSquare ? board[squareToIndex(dragFromSquare)] : null;

  useEffect(() => {
    if (!dragFromSquare) {
      setDragPointer(null);
    }
  }, [dragFromSquare]);

  const handleBoardPointerMove = (event) => {
    if (dragFromSquare) {
      const coords = pointerEventToCoords(event, size);
      if (coords) {
        setDragPointer(coords);
      }
    }

    const square = pointerEventToSquare(event, size, orientation);
    if (!square) {
      onSquareHover?.(null);
      return;
    }
    onSquareHover?.(square);
    onSquareEnter?.(square);
  };

  const handleBoardPointerUp = (event) => {
    const coords = pointerEventToCoords(event, size);
    if (coords) {
      setDragPointer(coords);
    }

    const square = pointerEventToSquare(event, size, orientation);
    if (square) {
      if (!dragFromSquare || dragFromSquare === square) {
        onSquareTap?.(square);
      }
      onSquareUp?.(square);
    } else if (dragFromSquare) {
      onSquareUp?.(dragFromSquare);
    }

    if (event.currentTarget.releasePointerCapture) {
      try {
        event.currentTarget.releasePointerCapture(event.pointerId);
      } catch {
        // Ignore pointer capture release errors.
      }
    }
  };

  return (
    <svg
      className="board"
      viewBox={`0 0 ${size} ${size}`}
      role="img"
      aria-label="Chess board"
      onPointerMove={handleBoardPointerMove}
      onPointerUp={handleBoardPointerUp}
      onPointerLeave={() => onSquareHover?.(null)}
    >
      <defs>
        <linearGradient id="lightSquare" x1="0" x2="0" y1="0" y2="1">
          <stop offset="0%" stopColor="#f0d9b5" />
          <stop offset="100%" stopColor="#f0d9b5" />
        </linearGradient>
        <linearGradient id="darkSquare" x1="0" x2="0" y1="0" y2="1">
          <stop offset="0%" stopColor="#b58863" />
          <stop offset="100%" stopColor="#b58863" />
        </linearGradient>
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
        const isTracked = trackedSquare === square;
        const isDragFrom = dragFromSquare === square;
        const isDragTo = dragToSquare === square;
        const heat = heatmap[square] || 0;

        return (
          <g
            key={square}
            onPointerDown={(event) => {
              const svg = event.currentTarget.ownerSVGElement;
              if (svg?.setPointerCapture) {
                svg.setPointerCapture(event.pointerId);
              }
              onSquareDown?.(square, event);
            }}
            onPointerEnter={() => {
              onSquareHover?.(square);
              onSquareEnter?.(square);
            }}
            style={{ cursor: "pointer" }}
          >
            <rect x={x} y={y} width={cell} height={cell} fill={isLight ? "url(#lightSquare)" : "url(#darkSquare)"} />

            {heat !== 0 && (
              <rect
                x={x + 1.5}
                y={y + 1.5}
                width={cell - 3}
                height={cell - 3}
                fill={heatColor(heat)}
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
                stroke="#d3cf72"
                strokeWidth="3"
                opacity="0.9"
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
                strokeWidth="3"
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
                strokeWidth="3"
              />
            )}

            {isTracked && (
              <rect
                x={x + 3}
                y={y + 3}
                width={cell - 6}
                height={cell - 6}
                fill="none"
                stroke="#c6a25a"
                strokeWidth="3.2"
                opacity="0.95"
              />
            )}

            {isDragFrom && (
              <rect
                x={x + 6}
                y={y + 6}
                width={cell - 12}
                height={cell - 12}
                fill="none"
                stroke="#4f7234"
                strokeWidth="3"
                opacity="0.85"
              />
            )}

            {isDragTo && (
              <rect
                x={x + 8}
                y={y + 8}
                width={cell - 16}
                height={cell - 16}
                fill="none"
                stroke="#9bc26a"
                strokeWidth="3"
                opacity="0.9"
              />
            )}

            {isTarget && (
              <circle cx={x + cell / 2} cy={y + cell / 2} r={cell * 0.14} fill="#6f9d4f" opacity="0.88" />
            )}

            {isHovered && (
              <rect
                x={x + 10}
                y={y + 10}
                width={cell - 20}
                height={cell - 20}
                fill="none"
                stroke="#66635d"
                strokeWidth="2"
                opacity="0.7"
              />
            )}
          </g>
        );
      })}

      {arrows.map((arrow, idx) => {
        const from = squareToDisplayCoords(arrow.from, size, orientation);
        const to = squareToDisplayCoords(arrow.to, size, orientation);
        const geometry = arrowGeometry(from, to, cell);
        if (!geometry) return null;
        const color = arrow.color || "#c6a25a";
        const width = Math.max(4, arrow.width || 8);
        const opacity = arrow.opacity || 0.82;
        return (
          <g key={`${arrow.from}-${arrow.to}-${idx}`}>
            <line
              x1={geometry.sx}
              y1={geometry.sy}
              x2={geometry.ex}
              y2={geometry.ey}
              stroke="#111111"
              strokeWidth={width + 3}
              strokeLinecap="round"
              opacity={Math.min(0.5, opacity)}
            />
            <line
              x1={geometry.sx}
              y1={geometry.sy}
              x2={geometry.ex}
              y2={geometry.ey}
              stroke={color}
              strokeWidth={width}
              strokeLinecap="round"
              opacity={opacity}
            />
            <polygon
              points={`${geometry.tipX},${geometry.tipY} ${geometry.leftX},${geometry.leftY} ${geometry.rightX},${geometry.rightY}`}
              fill={color}
              opacity={opacity}
            />
            <circle cx={geometry.sx} cy={geometry.sy} r={Math.max(2.4, width * 0.32)} fill={color} opacity={opacity} />
          </g>
        );
      })}

      {Array.from({ length: 64 }).map((_, displayIndex) => {
        const boardIndex = displaySquareToBoardIndex(displayIndex, orientation);
        const square = indexToSquare(boardIndex);
        if (dragFromSquare && square === dragFromSquare && draggedPiece) {
          return null;
        }

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

      {draggedPiece && dragPointer && (
        <g className="drag-piece" transform={`translate(${dragPointer.x} ${dragPointer.y})`}>
          <image
            x={-(cell - 6) / 2}
            y={-(cell - 6) / 2}
            width={cell - 6}
            height={cell - 6}
            href={`/pieces/cburnett/${pieceAssetName(draggedPiece)}.svg`}
            preserveAspectRatio="xMidYMid meet"
            pointerEvents="none"
          />
        </g>
      )}

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
