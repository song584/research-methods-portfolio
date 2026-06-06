# Research Methods Portfolio

This repository organizes selected research workflows from psychology and neuroimaging projects.

The current focus is not to expose private study data. Instead, each workflow uses sanitized or synthetic examples to demonstrate reusable analysis logic that reflects work performed in prior projects.

## Repository Map

- `projects/`: short project pages that summarize research context and link to related workflow demos.
- `workflows/`: runnable code demos for data processing, analysis, modeling, and visualization.

## Project-To-Workflow Map

| Project | Workflow demo | What it demonstrates |
| --- | --- | --- |
| `projects/alzheimer_morphological_similarity_network/` | `workflows/ad_mri_similarity_network_demo/` | Structural MRI feature handling, cortical similarity networks, graph features, classifier evaluation, and stratified 5-fold cross-validation. |

## How To Run

The current workflow uses only `numpy` and `pandas`.

```bash
cd workflows/ad_mri_similarity_network_demo
python -m pip install -r requirements.txt
python scripts/run_demo.py
```

The demo writes synthetic example data, metric tables, and SVG figures into the workflow folder.

## Data Policy

Original participant-level data, protected health information, and unpublished study files are not included. Demo datasets are synthetic or sanitized and are provided only to show the analysis workflow.
