# Input format: `numpos.csv`

The fitting scripts start from response counts rather than raw response logs.
Any preprocessing that produces the table below will work.

## What the table holds

One row per participant and condition, giving the number of positive responses
at each of seven stimulus levels.

- CSV, UTF-8, one header row
- Rows = participants × conditions (16 participants × 9 conditions = 144 rows)

| Column | Type | Meaning |
| --- | --- | --- |
| `participant` | string | Participant identifier; passed through to the results |
| `stim_type` | integer or string | Grouping label; passed through, not used in fitting |
| `cond` | string | Condition name; passed through |
| `label` | string | Unique row label such as `1facing`; passed through |
| `k1`–`k7` | integer 0–20 | Positive responses at each stimulus level |

## Stimulus levels

`k1`–`k7` must follow the same order as `StimLevels` in `fit_pse.m`:

```matlab
StimLevels = [-42 -28 -14 0 14 28 42];   % k1 = -42 ms, ..., k7 = 42 ms
OutOfNum   = [20 20 20 20 20 20 20];     % 20 trials per level, so k is 0-20
```

Units and sign are whatever the experiment used, as long as `StimLevels`
matches. Which of the two responses counts as positive determines the sign of
the PSE; the only requirement is that it is counted consistently. If a level has
a different number of trials, change `OutOfNum` to match.

## Where it goes

`fit_pse.m` reads `outputs/numpos.csv`. Put the file there, or change `in_csv`
at the top of the script.

## Example

From `numpos_example.csv`, which contains made-up values for illustration:

```
participant,stim_type,cond,label,k1,k2,k3,k4,k5,k6,k7
P01_example,0,none,0none,2,5,11,16,18,20,20
P01_example,1,BB,1BB,2,5,10,14,18,19,20
P01_example,1,facing,1facing,2,4,8,12,19,19,20
```

## Output

`fit_pse.m` writes `outputs/pse_results.csv`:

| Column | Meaning |
| --- | --- |
| `participant`, `stim_type`, `cond`, `label` | Passed through from the input |
| `alpha`, `beta` | Fitted threshold and slope |
| `LL`, `exitflag` | Log likelihood and convergence flag (1 = converged) |
| `PSE` | Point of subjective equality |
