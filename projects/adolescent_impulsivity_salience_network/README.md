# Adolescent Impulsivity and the Salience Network

## Project Summary

This project looked for behavioural and neural markers of impulsivity in
adolescents. Participants performed three memory tasks — immediate (IMT),
delayed (DMT), and a similar-distractor variant (SMT) — each containing target
trials that required a response and target-like catch trials that required
withholding one. Task performance was related to trait impulsivity and to
salience-network connectivity measured with task-based and resting-state fMRI.

Published as: Kim JC, Song KS, et al. *The role of the salience network in
adolescent impulsivity using memory tasks and neuroimaging.* Communications
Medicine (2025). https://doi.org/10.1038/s43856-025-01212-y

## My Role

- Prepared and checked the behavioural response data across the three tasks.
- Specified and fitted the linear mixed-effects models for error rate,
  reaction time, and rate correct score.
- Derived Type III tests, estimated marginal means, pairwise contrasts, and
  partial eta squared, and assembled the result tables used for reporting.
- Ran the partial correlation analyses relating behaviour to impulsivity
  scores with age and sex controlled.
- Contributed to manuscript writing and revision.

## Methods Used

- Repeated-measures behavioural design (task x stimulus type)
- Linear mixed-effects models with participant random intercepts (`lme4`)
- Satterthwaite-based Type III tests (`lmerTest`)
- Estimated marginal means and contrasts (`emmeans`)
- Partial eta squared from F ratios
- Partial correlation controlling for age and sex

## Related Workflow

The modelling code is published as a workflow:

```text
../../workflows/lmm_behavioral_imt/
```

The workflow covers the modelling stage and takes a long-form response table
as its input. Participant-level data are not included.
