#!/usr/bin/env python3
"""Summarise and plot the PSE estimates produced by the fitting step.

Reads outputs/pse_results.csv, drops failed fits, and writes a condition
summary, a long table, and bar plots.

Run: python after_pse_analysis.py
"""

import os
import re

import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

# Cleaning and exclusion settings.
EXCEPT_NONE = True             # leave the baseline condition out of plots and summaries
EXCLUDE_PARTICIPANTS = []      # e.g. ["P12"]
PSE_ABS_LIMIT = 100.0          # treat |PSE| above this as a failed fit; None disables
DROP_NONFINITE = True

HERE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.join(HERE, "outputs")
FIGDIR = os.path.join(OUTDIR, "figures")

STIM_MAP = {0: "none", 1: "arrow", 2: "gaze"}
LABEL_RE = re.compile(r"^(.+?)([012])(none|BB|facing|FF|nonfacing)$")


def load_long():
    """Return the PSE estimates as [participant, stim_type, confront, pse, exitflag]."""
    long_csv = os.path.join(OUTDIR, "pse_results.csv")
    wide_csv = os.path.join(HERE, "_original_reference", "pses.csv")

    if os.path.exists(long_csv):
        d = pd.read_csv(long_csv)
        d["stim_type"] = d["stim_type"].map(STIM_MAP)
        d = d.rename(columns={"cond": "confront", "PSE": "pse"})
        if "exitflag" not in d:
            d["exitflag"] = 1
        return d[["participant", "stim_type", "confront", "pse", "exitflag"]], long_csv

    # Fall back to a wide table with one column per participant and condition,
    # named PSE<participant><stimulus><condition>.
    raw = pd.read_csv(wide_csv)
    rows = []
    for col in raw.columns:
        name = col.strip()
        if not name.startswith("PSE"):
            continue
        m = LABEL_RE.match(name[3:])
        if not m:
            continue
        pid, stim, cond = m.group(1), int(m.group(2)), m.group(3)
        rows.append({"participant": pid, "stim_type": STIM_MAP[stim],
                     "confront": cond, "pse": float(raw[col].iloc[0]),
                     "exitflag": 1})
    return pd.DataFrame(rows), wide_csv


def clean(df):
    """Drop failed fits and excluded participants; return the row counts too."""
    n0 = len(df)
    d = df.copy()
    if DROP_NONFINITE:
        d = d[np.isfinite(d["pse"])]
    if PSE_ABS_LIMIT is not None:
        d = d[d["pse"].abs() <= PSE_ABS_LIMIT]
    if "exitflag" in d:
        d = d[d["exitflag"] == 1]
    if EXCLUDE_PARTICIPANTS:
        d = d[~d["participant"].isin(EXCLUDE_PARTICIPANTS)]
    return d.reset_index(drop=True), n0, len(d)


def summarize(d):
    """Mean, SD, N and standard error per stimulus type and direction pairing."""
    g = (d.groupby(["stim_type", "confront"])["pse"]
           .agg(["mean", "std", "count"]).reset_index())
    g["se"] = g["std"] / np.sqrt(g["count"])
    return g


def diff_from_baseline(d):
    """PSE relative to each participant's baseline condition."""
    base = (d[d["stim_type"] == "none"]
            .groupby("participant")["pse"].mean().rename("base"))
    m = d[d["stim_type"] != "none"].merge(base, on="participant", how="left")
    m["pse_diff"] = m["pse"] - m["base"]
    return m


def barplot(d, x, hue, fname, title):
    plt.figure(figsize=(7, 5))
    sns.barplot(x=x, y="pse", hue=hue, data=d, errorbar="se",
                capsize=0.1, palette="Blues", err_kws={"linewidth": 1.2})
    plt.ylabel("PSE (ms)")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(os.path.join(FIGDIR, fname), dpi=120)
    plt.close()


def main():
    os.makedirs(FIGDIR, exist_ok=True)
    df, src = load_long()
    print(f"read {len(df)} rows from {src}")

    d, n0, n1 = clean(df)
    print(f"kept {n1} of {n0} rows after removing failed fits and exclusions")

    plot_d = d[d["stim_type"] != "none"] if EXCEPT_NONE else d

    summ = summarize(plot_d)
    diff = diff_from_baseline(d)
    d.to_csv(os.path.join(OUTDIR, "pse_long.csv"), index=False)
    with pd.ExcelWriter(os.path.join(OUTDIR, "summary_pse.xlsx")) as xw:
        summ.to_excel(xw, sheet_name="mean_by_condition", index=False)
        diff.to_excel(xw, sheet_name="diff_from_baseline", index=False)
        d.to_excel(xw, sheet_name="pse_long", index=False)

    barplot(plot_d, "confront", "stim_type", "pse_by_confront.png",
            "PSE by direction pairing and cue type")
    barplot(plot_d, "stim_type", "confront", "pse_by_stim_type.png",
            "PSE by cue type and direction pairing")

    print(f"wrote {os.path.join(OUTDIR, 'summary_pse.xlsx')}")
    print(f"wrote {os.path.join(OUTDIR, 'pse_long.csv')}")
    print(f"wrote figures to {FIGDIR}")
    print("\nMean PSE (ms) by condition:")
    print(summ.to_string(index=False))


if __name__ == "__main__":
    main()
