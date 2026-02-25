import { useMemo, useState } from "react";

import ChessBoard from "./components/ChessBoard";

const DEFAULT_FEN = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1";

export default function App() {
  const [fen, setFen] = useState(DEFAULT_FEN);
  const [depth, setDepth] = useState(5);

  const topCandidates = useMemo(
    () => [
      { move: "c7c5", score: 22 },
      { move: "e7e5", score: 16 },
      { move: "g8f6", score: 11 },
      { move: "d7d5", score: 8 }
    ],
    []
  );

  const arrows = topCandidates.slice(0, 2).map((candidate) => ({
    from: candidate.move.slice(0, 2),
    to: candidate.move.slice(2, 4)
  }));

  return (
    <div className="page">
      <header className="hero">
        <h1>Chess Engine Visualization</h1>
        <p>Live principal variation, candidate ranking, and search telemetry.</p>
      </header>

      <main className="layout">
        <section className="panel board-panel">
          <ChessBoard fen={fen} arrows={arrows} />
        </section>

        <section className="panel controls">
          <label>
            FEN
            <textarea value={fen} onChange={(event) => setFen(event.target.value)} rows={3} />
          </label>

          <label>
            Max depth: <strong>{depth}</strong>
            <input
              type="range"
              min="1"
              max="8"
              value={depth}
              onChange={(event) => setDepth(Number(event.target.value))}
            />
          </label>

          <div className="stats-grid">
            <article>
              <span>Depth</span>
              <strong>{depth}</strong>
            </article>
            <article>
              <span>Nodes</span>
              <strong>1.2M</strong>
            </article>
            <article>
              <span>NPS</span>
              <strong>312k</strong>
            </article>
            <article>
              <span>Eval</span>
              <strong>+0.22</strong>
            </article>
          </div>

          <div className="candidates">
            <h2>Top Candidates</h2>
            {topCandidates.map((candidate, idx) => (
              <div className="candidate-row" key={candidate.move}>
                <span>#{idx + 1}</span>
                <span>{candidate.move}</span>
                <strong>{candidate.score > 0 ? `+${candidate.score}` : candidate.score}</strong>
              </div>
            ))}
          </div>
        </section>
      </main>
    </div>
  );
}
