# Research Methods Portfolio

This repository organizes selected research workflows from psychology and neuroimaging projects.

The current focus is not to expose private study data. Instead, each workflow uses sanitized or synthetic examples to demonstrate reusable analysis logic that reflects work performed in prior projects.

## Repository Map

- `projects/`: short project pages that summarize research context and link to related workflow demos.
- `workflows/`: runnable code demos for data processing, analysis, modeling, and visualization.

## Project-To-Workflow Map

| Project | Workflow | What it demonstrates |
| --- | --- | --- |
| `projects/alzheimer_morphological_similarity_network/` | `workflows/ad_mri_similarity_network_demo/` | Structural MRI feature handling, cortical similarity networks, graph features, classifier evaluation, and stratified 5-fold cross-validation. |
| `projects/temporal_order_judgment_pse/` | `workflows/pse_fitting_toj/` | Psychometric function fitting of temporal order judgments, point of subjective equality estimation, bootstrap goodness-of-fit, and condition-wise summaries. |

## Workflows

Each workflow folder is self-contained and carries its own README, inputs, and
run instructions. They differ in what they need to run:

| Workflow | Language | Requires |
| --- | --- | --- |
| `ad_mri_similarity_network_demo/` | Python | `numpy`, `pandas` |
| `pse_fitting_toj/` | MATLAB + Python | MATLAB with the Palamedes toolbox; `pandas`, `numpy`, `matplotlib`, `seaborn`, `openpyxl` |

The MRI workflow ships synthetic data and runs end to end:

```bash
cd workflows/ad_mri_similarity_network_demo
python -m pip install -r requirements.txt
python scripts/run_demo.py
```

It writes synthetic example data, metric tables, and SVG figures into the
workflow folder. The PSE workflow takes a response-count table as input and is
described in its own README.

## Data Policy

Original participant-level data, protected health information, and unpublished study files are not included. Demo datasets are synthetic or sanitized and are provided only to show the analysis workflow.
