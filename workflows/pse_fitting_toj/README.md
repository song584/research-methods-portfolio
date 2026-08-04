# PSE Fitting for Temporal Order Judgments

Estimates the point of subjective equality (PSE) for each participant and
condition in a temporal order judgment task by fitting a psychometric function,
then summarises and plots the estimates.

The input is a single table of response counts (`numpos.csv`). Preprocessing of
raw response logs is not included, since its shape depends on how the task was
run.

## Contents

```
.
├── README.md
├── INPUT_FORMAT.md         input file specification
├── numpos_example.csv      example input
├── fit_pse.m               numpos.csv -> cumulative-normal fit -> PSE   (MATLAB + Palamedes)
├── goodness_of_fit.m       bootstrap goodness-of-fit                    (MATLAB + Palamedes)
├── after_pse_analysis.py   PSE cleanup, summary table, bar plots        (Python)
└── outputs/                where the input goes and results are written
```

## Input

`numpos.csv` holds, for each participant and condition, the number of positive
responses at each of seven stimulus levels.

- Specification: [`INPUT_FORMAT.md`](./INPUT_FORMAT.md)
- Template: [`numpos_example.csv`](./numpos_example.csv)
- Location: `outputs/numpos.csv`, or change `in_csv` in `fit_pse.m`

## Requirements

- MATLAB with the [Palamedes toolbox](http://www.palamedestoolbox.org) for fitting
- Python with `pandas`, `numpy`, `matplotlib`, `seaborn`, `openpyxl` for the summaries

## Running

1. Put `numpos.csv` in `outputs/`.
2. In MATLAB, add Palamedes to the path: `addpath(genpath('<Palamedes>'))`
3. Fit: `run fit_pse.m` → `outputs/pse_results.csv`
4. Goodness of fit: `run goodness_of_fit.m` → `outputs/pdev_results.csv`
5. Summaries: `python after_pse_analysis.py` → `outputs/summary_pse.xlsx`, `outputs/figures/*.png`

To try it out, copy `numpos_example.csv` to `outputs/numpos.csv` and run step 3.

## Fitting settings

```matlab
StimLevels  = [-42 -28 -14 0 14 28 42];   % stimulus onset asynchrony (ms)
OutOfNum    = [20 20 20 20 20 20 20];     % trials per level
PF          = @PAL_CumulativeNormal;
paramsFree  = [1 1 0 0];                  % threshold and slope free; guess 0, lapse 0.01 fixed
searchGrid.alpha = -42:0.1:42;
searchGrid.beta  = 10.^(-2.5:0.001:1.5);
```

PSE is the stimulus value where the fitted function reaches 0.5, obtained from
`PAL_CumulativeNormal([alpha beta 0 0.01], 0.5, 'inverse')`. The sign convention
of `StimLevels` sets the sign of the PSE, so flip it if the estimates come out
opposite to what the task design implies.

## Outputs

| File | Contents |
| --- | --- |
| `pse_results.csv` | `alpha`, `beta`, `LL`, `exitflag`, `PSE` per participant and condition |
| `pdev_results.csv` | bootstrap `pDev`; small values indicate poor fit |
| `summary_pse.xlsx`, `pse_long.csv` | condition summaries and the cleaned estimates |
| `figures/pse_by_confront.png`, `figures/pse_by_stim_type.png` | condition bar plots |

`after_pse_analysis.py` drops failed fits and applies exclusions through options
at the top of the file: `PSE_ABS_LIMIT` and `DROP_NONFINITE` remove estimates
outside the stimulus range or non-finite values, `EXCEPT_NONE` and
`EXCLUDE_PARTICIPANTS` remove a baseline condition or specific participants.

## Study context

The background to this analysis is described in the project page:

```text
projects/temporal_order_judgment_pse/
```

Raw responses, preprocessing, and the experiment program are not included.
