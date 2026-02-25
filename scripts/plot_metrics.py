#!/usr/bin/env python3
"""Render JANUS benchmark charts from CSV metrics into SVG."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]

PALETTE = {
    "bg": "#161616",
    "panel": "#1e1e1e",
    "grid": "#2b2b2b",
    "text": "#e6e2d8",
    "muted": "#bdb8ad",
    "gold": "#c6a25a",
    "red": "#7d2a2a",
    "green": "#4e7d49",
}


def _load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Plot JANUS benchmark metrics")
    parser.add_argument(
        "--metrics-dir",
        default=str(ROOT / "docs" / "metrics"),
        help="Directory containing benchmark CSV files",
    )
    parser.add_argument(
        "--output",
        default=str(ROOT / "docs" / "visuals" / "performance-charts.svg"),
        help="Output SVG path",
    )
    return parser.parse_args()


def plot(perft_rows: list[dict[str, str]], search_rows: list[dict[str, str]], output: Path) -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.facecolor": PALETTE["panel"],
            "figure.facecolor": PALETTE["bg"],
            "axes.edgecolor": PALETTE["grid"],
            "axes.labelcolor": PALETTE["text"],
            "xtick.color": PALETTE["muted"],
            "ytick.color": PALETTE["muted"],
            "text.color": PALETTE["text"],
            "axes.titlecolor": PALETTE["text"],
            "grid.color": PALETTE["grid"],
        }
    )

    fig, axes = plt.subplots(1, 2, figsize=(16, 6), dpi=150)
    fig.suptitle("JANUS Performance Snapshot", fontsize=18, fontweight="bold", color=PALETTE["text"])

    # Perft NPS by depth and position.
    perft_by_pos: dict[str, list[tuple[int, int]]] = defaultdict(list)
    for row in perft_rows:
        perft_by_pos[row["position"]].append((int(row["depth"]), int(row["nps"])))

    ax0 = axes[0]
    colors = [PALETTE["gold"], PALETTE["red"], PALETTE["green"]]
    for idx, (position, data) in enumerate(sorted(perft_by_pos.items())):
        data.sort(key=lambda x: x[0])
        depths = [d for d, _ in data]
        nps = [v for _, v in data]
        ax0.plot(depths, nps, marker="o", linewidth=2.5, color=colors[idx % len(colors)], label=position)

    ax0.set_title("Perft Nodes/Second by Depth")
    ax0.set_xlabel("Depth")
    ax0.set_ylabel("NPS")
    ax0.grid(True, alpha=0.6)
    ax0.legend(frameon=False)

    # Search NPS by depth limit (start position).
    search_by_pos: dict[str, list[tuple[int, int, int]]] = defaultdict(list)
    for row in search_rows:
        search_by_pos[row["position"]].append(
            (int(row["depth_limit"]), int(row["nps"]), int(row["nodes"]))
        )

    ax1 = axes[1]
    for idx, (position, data) in enumerate(sorted(search_by_pos.items())):
        data.sort(key=lambda x: x[0])
        depth_limits = [d for d, _, _ in data]
        nps = [v for _, v, _ in data]
        ax1.plot(depth_limits, nps, marker="s", linewidth=2.5, color=colors[idx % len(colors)], label=f"{position} nps")

    ax1.set_title("Search Nodes/Second by Depth Limit")
    ax1.set_xlabel("Depth limit")
    ax1.set_ylabel("NPS")
    ax1.grid(True, alpha=0.6)
    ax1.legend(frameon=False)

    output.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(output, format="svg")
    plt.close(fig)


def main() -> None:
    args = parse_args()
    metrics_dir = Path(args.metrics_dir)
    output = Path(args.output)

    perft_rows = _load_csv(metrics_dir / "perft_metrics.csv")
    search_rows = _load_csv(metrics_dir / "search_metrics.csv")
    plot(perft_rows, search_rows, output)
    print(f"wrote {output}")


if __name__ == "__main__":
    main()
