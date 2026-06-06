# AD MRI Similarity Network Demo

This workflow is a cleaned, public-safe version of analysis logic extracted from an exploratory AD/MCI multimodal notebook.

It demonstrates how structural MRI-derived regional measures can be converted into subject-level cortical similarity networks, summarized into graph features, and used in a simple diagnostic classification pipeline.

## What This Demo Shows

- Structural MRI feature table handling
- Cortical-thickness similarity matrix construction
- Cost-based binary network thresholding
- Node-level network feature extraction
- Structural and network feature concatenation
- Logistic regression and nearest-centroid classification
- Performance reporting with accuracy, sensitivity, specificity, AUC, and F1
- 5-fold stratified cross-validation without external ML dependencies

## What This Demo Does Not Include

- Original participant-level data
- Original private Excel files
- Full paper/poster reproduction
- Medical or clinical model deployment

The included data generator creates synthetic structural features with AD-like group differences for demonstration only.

## Source Context

The cleaned code was derived from a local exploratory AD/MCI multimodal analysis notebook. The original notebook and study data are not included in this repository.

Relevant notebook sections included:

- dataset filtering and label checks
- cortical thickness similarity network construction
- graph-theory feature extraction
- HC vs AD / MCI classification experiments
- exploratory GCN/GAT graph classification trials

## Run

From this folder:

```bash
python -m pip install -r requirements.txt
python scripts/run_demo.py
```

Expected outputs:

```text
examples/synthetic_structural_mri.csv
figures/group_mean_similarity_matrices.svg
figures/classification_performance.svg
figures/cv_classification_performance.svg
```

## Relation To Project Portfolio

This workflow supports the project page:

```text
projects/alzheimer_morphological_similarity_network/
```

The demo reflects the type of analysis workflow used in the project with synthetic data, not the original study dataset.

## Dependencies

The demo intentionally uses a minimal dependency set:

```text
numpy
pandas
```

The exploratory notebook used additional libraries such as scikit-learn, NetworkX, SHAP, and PyTorch Geometric. Those are not required for this public-safe demo.
