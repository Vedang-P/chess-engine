# JANUS Visual Assets

All repository visuals live in this folder and use a shared visual style:

- Background: `#161616`
- Panels: `#1e1e1e`
- Borders/grid: `#2b2b2b`
- Primary text: `#e6e2d8`
- Accent: `#c6a25a`
- Accent red: `#7d2a2a`

## Core diagrams
- `architecture.svg`
- `search-lifecycle.svg`
- `movegen-pipeline.svg`
- `evaluation-breakdown.svg`
- `performance-charts.svg`

## Demo GIFs
- `demo-play-engine.gif`
- `demo-heatmap-toggle.gif`
- `demo-dynamic-value.gif`

## Regenerate metrics + charts + GIFs
From repository root:

```bash
python3 scripts/bench.py
python3 scripts/plot_metrics.py
python3 scripts/generate_demo_gifs.py
```

## Editing workflow (professional tools)
- Use Mermaid in README for fast text-based diagrams.
- Use Figma or diagrams.net to iterate visual composition, then export SVG.
- Keep line weights and spacing consistent across all assets.
