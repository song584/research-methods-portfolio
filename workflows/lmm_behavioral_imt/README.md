# Mixed-Effects Models of Memory-Task Behaviour

Fits linear mixed-effects models to performance on three memory tasks (IMT,
DMT, SMT). Task and stimulus type are fixed effects, age and sex are
covariates, and participants get a random intercept.

The input is a long-form table of condition-level values. Preprocessing of raw
task logs is not included.

## Contents

```
.
├── README.md
├── INPUT_FORMAT.md              input file specification
├── example_error_rate_long.csv  example input
├── lmm_common.R                 packages, data coding, table helpers
├── lmm_error_rate.R             error rate   ~ stimulus * task + Gender + Age
├── lmm_rt.R                     reaction time ~ stimulus * task + Gender + Age
├── lmm_rcs.R                    rate correct  ~ task + Gender + Age
└── outputs/                     where the input goes and results are written
```

## Models

```r
# Error rate and reaction time are measured on both target and catch trials
measure ~ stimulus * task + Gender + Age + (1 | subject)

# Rate correct score is defined on target trials only, so there is no
# stimulus factor and no interaction
measure ~ task + Gender + Age + (1 | subject)
```

Models are fitted with `lme4` and tested with `lmerTest`, which gives Type III
tests on Satterthwaite degrees of freedom. Partial eta squared comes from the F
ratio:

```
eta2_p = (F * NumDF) / (F * NumDF + DenDF)
```

Where the interaction qualifies the task effect, the task contrast is also
reported within each stimulus type. These come from `joint_tests(model, by =
"stimulus")` on the full model rather than from separate fits per stimulus
type, so the same error term applies throughout.

## Requirements

R with `tidyverse`, `lme4`, `lmerTest`, `broom.mixed`, `emmeans`, `gridExtra`.

```r
install.packages(c("tidyverse", "lme4", "lmerTest",
                   "broom.mixed", "emmeans", "gridExtra"))
```

## Running

Put the input CSV in `outputs/` under the name given in
[`INPUT_FORMAT.md`](./INPUT_FORMAT.md), then run from this folder:

```bash
Rscript lmm_error_rate.R
Rscript lmm_rt.R
Rscript lmm_rcs.R
```

To try it out, copy `example_error_rate_long.csv` to
`outputs/error_rate_long.csv` and run the first script.

## Outputs

Written to `outputs/`, one set per measure:

| File | Contents |
| --- | --- |
| `typeIII_anova_*.csv` | Type III ANOVA with partial eta squared |
| `fixed_effects_*.csv` | Estimates, 95% confidence intervals, t, p |
| `emmeans_*.csv` | Estimated marginal means |
| `pairwise_*.csv` | Uncorrected pairwise contrasts |
| `task_within_stimulus_*.csv` | Task effect within each stimulus type (error rate and reaction time) |
| `lmm_report_*.pdf` | The tables above, one per page |

## Sex coding

`Gender` (or `Sex`) is read as 1 = male, 2 = female. Data using another coding
should be recoded before it goes in. The scripts stop if the coding does not
match, rather than silently dropping the participants that fall outside it.

## Study context

The background to this analysis is described in the project page:

```text
projects/adolescent_impulsivity_salience_network/
```

Participant-level data are not included.
