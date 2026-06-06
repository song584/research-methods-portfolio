from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def _write(path: str | Path, text: str) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _color(value: float, vmin: float, vmax: float) -> str:
    if vmax <= vmin:
        t = 0.5
    else:
        t = (value - vmin) / (vmax - vmin)
    t = float(np.clip(t, 0, 1))
    # Blue-white-red ramp.
    if t < 0.5:
        k = t / 0.5
        r = int(245 * k + 49 * (1 - k))
        g = int(245 * k + 130 * (1 - k))
        b = int(245 * k + 189 * (1 - k))
    else:
        k = (t - 0.5) / 0.5
        r = int(220 * k + 245 * (1 - k))
        g = int(38 * k + 245 * (1 - k))
        b = int(38 * k + 245 * (1 - k))
    return f"rgb({r},{g},{b})"


def _heatmap_svg(matrix: np.ndarray, x: int, y: int, size: int, title: str, vmin: float, vmax: float) -> str:
    n = matrix.shape[0]
    cell = size / n
    parts = [f'<text x="{x}" y="{y - 12}" class="title">{title}</text>']
    for i in range(n):
        for j in range(n):
            parts.append(
                f'<rect x="{x + j * cell:.2f}" y="{y + i * cell:.2f}" '
                f'width="{cell + 0.2:.2f}" height="{cell + 0.2:.2f}" '
                f'fill="{_color(float(matrix[i, j]), vmin, vmax)}"/>'
            )
    parts.append(
        f'<rect x="{x}" y="{y}" width="{size}" height="{size}" '
        'fill="none" stroke="#334155" stroke-width="1"/>'
    )
    return "\n".join(parts)


def plot_group_mean_networks(
    weighted_networks: np.ndarray,
    labels: np.ndarray,
    output_path: str | Path,
) -> None:
    """Save control, AD, and difference mean similarity matrices as SVG."""

    control_mean = weighted_networks[labels == 0].mean(axis=0)
    ad_mean = weighted_networks[labels == 3].mean(axis=0)
    diff = ad_mean - control_mean
    common_min = min(control_mean.min(), ad_mean.min())
    common_max = max(control_mean.max(), ad_mean.max())
    diff_abs = float(np.max(np.abs(diff)))

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="980" height="360" viewBox="0 0 980 360">
<style>
  .heading {{ font: 700 20px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; fill: #111827; }}
  .title {{ font: 650 14px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; fill: #334155; }}
  .note {{ font: 12px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; fill: #64748b; }}
</style>
<rect width="980" height="360" fill="#ffffff"/>
<text x="28" y="34" class="heading">Group mean cortical-thickness similarity matrices</text>
{_heatmap_svg(control_mean, 40, 78, 240, "Control mean", common_min, common_max)}
{_heatmap_svg(ad_mean, 370, 78, 240, "AD mean", common_min, common_max)}
{_heatmap_svg(diff, 700, 78, 240, "AD - Control", -diff_abs, diff_abs)}
<text x="40" y="342" class="note">Synthetic data demo; values do not represent real participants.</text>
</svg>'''
    _write(output_path, svg)


def plot_performance_table(
    performance: pd.DataFrame,
    output_path: str | Path,
) -> None:
    """Save a compact SVG bar plot of classifier metrics."""

    metrics = ["accuracy", "sensitivity", "specificity", "auc", "f1"]
    labels = [f"{r.feature_set}/{r.model}" for r in performance.itertuples()]
    colors = ["#2563eb", "#0f766e", "#7c3aed", "#f97316", "#be123c", "#334155"]

    width = 1080
    height = 430
    left = 70
    top = 78
    chart_h = 250
    group_w = 185
    bar_w = 18

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<style>.heading{font:700 20px -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;fill:#111827}.axis{font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;fill:#475569}.legend{font:11px -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;fill:#334155}</style>',
        f'<rect width="{width}" height="{height}" fill="#ffffff"/>',
        '<text x="28" y="34" class="heading">Demo classification performance</text>',
        f'<line x1="{left}" y1="{top + chart_h}" x2="{left + group_w * len(metrics)}" y2="{top + chart_h}" stroke="#334155"/>',
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + chart_h}" stroke="#334155"/>',
    ]

    for tick in [0, 0.25, 0.5, 0.75, 1.0]:
        y = top + chart_h * (1 - tick)
        parts.append(f'<line x1="{left - 5}" y1="{y:.1f}" x2="{left + group_w * len(metrics)}" y2="{y:.1f}" stroke="#e2e8f0"/>')
        parts.append(f'<text x="{left - 42}" y="{y + 4:.1f}" class="axis">{tick:.2f}</text>')

    for metric_i, metric in enumerate(metrics):
        gx = left + metric_i * group_w + 22
        parts.append(f'<text x="{gx}" y="{top + chart_h + 28}" class="axis">{metric}</text>')
        for row_i, row in enumerate(performance.itertuples()):
            score = float(getattr(row, metric))
            x = gx + row_i * (bar_w + 2)
            bar_h = chart_h * score
            y = top + chart_h - bar_h
            parts.append(
                f'<rect x="{x}" y="{y:.1f}" width="{bar_w}" height="{bar_h:.1f}" '
                f'fill="{colors[row_i % len(colors)]}"/>'
            )

    legend_x = 70
    legend_y = 365
    for i, label in enumerate(labels):
        x = legend_x + (i % 3) * 310
        y = legend_y + (i // 3) * 24
        parts.append(f'<rect x="{x}" y="{y - 12}" width="12" height="12" fill="{colors[i % len(colors)]}"/>')
        parts.append(f'<text x="{x + 18}" y="{y - 2}" class="legend">{label}</text>')

    parts.append("</svg>")
    _write(output_path, "\n".join(parts))


def plot_cv_performance_table(
    performance: pd.DataFrame,
    output_path: str | Path,
) -> None:
    """Save a compact SVG bar plot of cross-validated classifier metrics."""

    metrics = ["accuracy", "sensitivity", "specificity", "auc", "f1"]
    labels = [f"{r.feature_set}/{r.model}" for r in performance.itertuples()]
    colors = ["#2563eb", "#0f766e", "#7c3aed", "#f97316", "#be123c", "#334155"]

    width = 1080
    height = 460
    left = 70
    top = 80
    chart_h = 260
    group_w = 185
    bar_w = 18

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<style>.heading{font:700 20px -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;fill:#111827}.axis{font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;fill:#475569}.legend{font:11px -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;fill:#334155}.note{font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;fill:#64748b}</style>',
        f'<rect width="{width}" height="{height}" fill="#ffffff"/>',
        '<text x="28" y="34" class="heading">5-fold cross-validated demo performance</text>',
        f'<line x1="{left}" y1="{top + chart_h}" x2="{left + group_w * len(metrics)}" y2="{top + chart_h}" stroke="#334155"/>',
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + chart_h}" stroke="#334155"/>',
    ]

    for tick in [0, 0.25, 0.5, 0.75, 1.0]:
        y = top + chart_h * (1 - tick)
        parts.append(f'<line x1="{left - 5}" y1="{y:.1f}" x2="{left + group_w * len(metrics)}" y2="{y:.1f}" stroke="#e2e8f0"/>')
        parts.append(f'<text x="{left - 42}" y="{y + 4:.1f}" class="axis">{tick:.2f}</text>')

    for metric_i, metric in enumerate(metrics):
        gx = left + metric_i * group_w + 22
        parts.append(f'<text x="{gx}" y="{top + chart_h + 28}" class="axis">{metric}</text>')
        for row_i, row in enumerate(performance.itertuples()):
            mean = float(getattr(row, f"{metric}_mean"))
            std = float(getattr(row, f"{metric}_std"))
            x = gx + row_i * (bar_w + 2)
            bar_h = chart_h * mean
            y = top + chart_h - bar_h
            err = chart_h * std
            cx = x + bar_w / 2
            parts.append(
                f'<rect x="{x}" y="{y:.1f}" width="{bar_w}" height="{bar_h:.1f}" '
                f'fill="{colors[row_i % len(colors)]}"/>'
            )
            parts.append(
                f'<line x1="{cx:.1f}" y1="{max(top, y - err):.1f}" '
                f'x2="{cx:.1f}" y2="{min(top + chart_h, y + err):.1f}" '
                'stroke="#111827" stroke-width="1"/>'
            )

    legend_x = 70
    legend_y = 385
    for i, label in enumerate(labels):
        x = legend_x + (i % 3) * 310
        y = legend_y + (i // 3) * 24
        parts.append(f'<rect x="{x}" y="{y - 12}" width="12" height="12" fill="{colors[i % len(colors)]}"/>')
        parts.append(f'<text x="{x + 18}" y="{y - 2}" class="legend">{label}</text>')
    parts.append('<text x="70" y="442" class="note">Bars show mean across folds; whiskers show sample standard deviation.</text>')
    parts.append("</svg>")
    _write(output_path, "\n".join(parts))
