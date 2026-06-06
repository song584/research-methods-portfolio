# Extraction Map From Exploratory Notebook

Source notebook:

```text
Local exploratory AD/MCI multimodal analysis notebook; not included in this repository.
```

The original notebook mixes dataset auditing, exploratory plots, classical ML, SHAP attempts, and exploratory GNN trials. This folder extracts only the stable, reusable parts into a public-safe workflow.

## Extracted Parts

| Original notebook area | Cleaned location | Notes |
|---|---|---|
| Dataset availability and label checks | README/project page only | Private Excel-dependent logic was not included. |
| Cortical thickness similarity matrix | `src/ad_mri_similarity_network/features.py` | Derived from `extract_features` and `extract_features_with_adjmat`. |
| Cost thresholding | `features.py` | Converted into reusable helper functions. |
| Node-level path length and degree features | `features.py` | Reimplemented without NetworkX to reduce dependencies. |
| Structural + network feature concatenation | `features.py` | Exposed through `build_feature_sets`. |
| HC vs AD classifier evaluation | `src/ad_mri_similarity_network/models.py` | Public demo uses minimal numpy classifiers instead of scikit-learn. |
| Group mean similarity matrix visualization | `src/ad_mri_similarity_network/plotting.py` | Implemented as dependency-light SVG generation. |
| GCN/GAT exploratory work | Not included in runnable workflow | Kept as future extension because the notebook version contains repeated exploratory cells and unresolved tensor/output-shape errors. |

## Why The Public Demo Uses Synthetic Data

The original notebook depends on private participant-level Excel files and derived neuroimaging variables. Those files should not be uploaded to GitHub. The demo therefore generates synthetic FreeSurfer-like columns:

```text
{region}_thickness
{region}_volume
{region}_area
diagnosis
```

This preserves the analysis structure without exposing protected or unpublished data.

## What Was Intentionally Simplified

- Only binary `control` vs `AD` classification is shown.
- MCI subgroups are not included in the demo.
- SHAP and random forest exploration are not included.
- PyTorch Geometric GCN/GAT experiments are not included.
- The demo uses `numpy` and `pandas` only, so it is easy to run in a minimal environment.

## Portfolio Message

This workflow demonstrates that the original project involved more than passive analysis:

- multimodal dataset auditing
- structural MRI feature engineering
- subject-level similarity network construction
- graph-feature extraction
- classifier evaluation
- exploratory graph neural network modeling

For a GitHub portfolio, the current cleaned workflow should be presented as a sanitized demo of the analysis logic, not as a full reproduction of the original study.
