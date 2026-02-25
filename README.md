# Chess Engine + Live Visualization Platform

A performance-oriented classical chess engine in Python with:
- Bitboard board state
- Legal move generation
- Perft validation helpers
- Iterative deepening alpha-beta search
- FastAPI endpoints + WebSocket streaming
- React + SVG frontend scaffold for live visualization

## Project Structure

```
chess_engine/
├── engine/
│   ├── bitboards.py
│   ├── constants.py
│   ├── board.py
│   ├── move.py
│   ├── movegen.py
│   ├── perft.py
│   ├── search.py
│   ├── evaluation.py
│   └── instrumentation.py
├── api/
│   ├── server.py
│   └── websocket.py
├── frontend/
│   └── (Vite + React + SVG board UI)
├── tests/
│   ├── test_bitboards.py
│   ├── test_board_state.py
│   ├── test_movegen.py
│   ├── test_perft.py
│   └── test_search.py
└── main.py
```

## Engine Capabilities (Current)

- 12 piece bitboards + occupancy bitboards
- FEN parsing
- Reversible make/unmake with history
- Move generation supports:
  - Pawn moves, captures, promotions, en passant
  - Knight, bishop, rook, queen, king moves
  - Castling legality checks (path clear + attacked-square checks)
  - King-safety filtering to produce legal moves only
- Search:
  - Negamax alpha-beta pruning
  - Iterative deepening
  - Basic move ordering
  - PV/candidate tracking

## Validation

```bash
python3 -m pytest -q
```

Current status: `18 passed`.

Perft checks included:
- Start position: depth 1/2/3 = `20 / 400 / 8902`
- Kiwipete: depth 2 = `2039`

## CLI Usage

Print board from FEN:

```bash
python3 main.py --fen "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
```

Run perft:

```bash
python3 main.py perft 3
python3 main.py perft 2 --divide
```

Run search:

```bash
python3 main.py search --depth 5 --time 3000
```

## API (FastAPI)

Install backend deps:

```bash
pip install fastapi uvicorn pydantic
```

Run server:

```bash
uvicorn api.server:app --reload
```

Endpoints:
- `GET /health`
- `POST /analyze` body: `{ "fen": "...", "max_depth": 5, "time_limit_ms": 3000 }`
- `POST /perft` body: `{ "fen": "...", "depth": 3, "divide": false }`
- `WS /ws/search` live iteration stream

## Frontend (React + SVG)

```bash
cd frontend
npm install
npm run dev
```

The frontend currently includes:
- Custom SVG board renderer (no image assets)
- Candidate move arrows overlay
- Search stats panel + candidate ranking UI
- Responsive layout foundation for live telemetry integration

## Next Steps

- Transposition table + Zobrist hashing
- Quiescence search
- Better handcrafted eval (king safety, pawn structure, mobility)
- Wire frontend to `/ws/search` for real-time engine telemetry
- Deploy backend (Fly/Render/Railway) + frontend (Cloudflare Pages)
