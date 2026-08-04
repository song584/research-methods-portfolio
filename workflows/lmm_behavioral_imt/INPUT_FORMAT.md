# Input format

Each script reads one long-form CSV from `outputs/`. A row is one participant
in one condition.

| Script | Reads | Rows per participant |
| --- | --- | --- |
| `lmm_error_rate.R` | `outputs/error_rate_long.csv` | 3 tasks × 2 stimulus types = 6 |
| `lmm_rt.R` | `outputs/rt_long.csv` | 3 tasks × 2 stimulus types = 6 |
| `lmm_rcs.R` | `outputs/rcs_long.csv` | 3 tasks = 3 |

## Columns

| Column | Values | Meaning |
| --- | --- | --- |
| `id` | integer or string | Participant identifier, constant within participant |
| `task` | 1, 2, 3 | 1 = IMT, 2 = DMT, 3 = SMT |
| `stimulus` | 1, 2 | 1 = target, 2 = catch. Absent from the RCS file |
| `Gender` | 1, 2 | 1 = male, 2 = female. May also be named `Sex` |
| `Age` | numeric | Years |
| `trans1` | numeric | The outcome value; 9999 marks a missing response |

The sex column may be named `Gender`, `Sex`, `gender`, or `sex`, but the values
must be 1 for male and 2 for female. Recode other schemes before running.

What `trans1` holds depends on the script:

- error rate: proportion of trials answered incorrectly
- reaction time: correct responses on target trials, false alarms on catch trials, in milliseconds
- rate correct score: proportion correct divided by mean reaction time

## Missing values

Rows where `trans1` is 9999 are dropped. Missing values in `Gender`, `task`, or
`stimulus` stop the script instead, so that participants are not quietly left
out of the model.

## Example

`example_error_rate_long.csv` shows the layout with made-up values:

```
id,task,stimulus,Gender,Age,trans1
P001,1,1,1,15,0.0507
P001,1,2,1,15,0.1422
P001,2,1,1,15,0.0753
```
