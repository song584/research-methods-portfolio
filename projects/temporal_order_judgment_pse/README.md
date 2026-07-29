# Temporal Order Judgment and the Point of Subjective Equality

## Project Summary

This project asked whether the perceived timing of a visual event is fixed by
its physical onset or reconstructed by the context it appears in. Participants
judged the temporal order of a target presented along an apparent-motion path,
and the direction of the surrounding cues was varied. Perceived timing was
quantified per participant and condition as the point of subjective equality
(PSE) from a fitted psychometric function, so that shifts in perceived
simultaneity could be compared across cue types and direction combinations.

## My Role

- Designed the temporal order judgment task and its cue conditions.
- Collected and organised participant-level response data.
- Aggregated responses into per-condition counts at each stimulus onset
  asynchrony.
- Fitted cumulative-normal psychometric functions and estimated PSE for every
  participant and condition.
- Evaluated fit quality by bootstrap and set exclusion criteria for failed fits.
- Compared PSE across cue types and direction combinations, and prepared the
  figures and tables used for reporting.

## Methods Used

- Psychophysical task design (temporal order judgment)
- Response aggregation across stimulus onset asynchrony levels
- Maximum-likelihood psychometric function fitting (Palamedes, MATLAB)
- PSE estimation by inverting the fitted function at 0.5
- Bootstrap goodness-of-fit assessment
- Repeated-measures comparison and visualisation of condition effects

## Related Workflow

The fitting and post-fitting analysis code is published as a workflow:

```text
../../workflows/pse_fitting_toj/
```

The workflow contains the fitting stage onward and takes a response-count table
as its input. Raw participant data, preprocessing, and the experiment program
are not included.
