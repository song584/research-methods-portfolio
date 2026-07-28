# AD MRI Similarity Network Demo

This workflow is a cleaned, public-safe version of analysis logic extracted from an exploratory AD/MCI multimodal notebook.

It demonstrates how structural MRI-derived regional measures can be converted into subject-level cortical similarity networks, summarized into graph features, and used in a simple diagnostic classification pipeline.

## What This Demo Shows

- Structural MRI feature table handling
- Cortical-thickness similarity matrix construction
- Cost-based binary network thresholding
- Node-level network feature extraction
- Network connectivity reporting across a range of connection costs
- Structural and network feature concatenation
- Logistic regression and nearest-centroid classification
- Performance reporting with accuracy, sensitivity, specificity, AUC, and F1
- 5-fold stratified cross-validation without external ML dependencies

## Network Measures

Each participant's cortical-thickness similarity matrix is thresholded into a
binary network at a given connection cost, and two nodal measures are extracted
per region:

| Measure | Definition |
| --- | --- |
| `ND` — nodal degree | `K_i = sum_j b_ij` |
| `NE` — nodal efficiency | `E_i = sum_{j != i} (1 / L_ij) / (V - 1)` |

The source analysis this workflow is drawn from used nodal path length,
`L_i = sum_{j != i} L_ij / (V - 1)` (Zhang et al., 2021). That measure averages
distances and is therefore defined only while every region can be reached from
every other. Thresholded cortical thickness networks are not guaranteed to meet
that condition: at the connection costs used here they separate into components,
and a region can end up with no connections at all. Nodal efficiency averages
`1 / L_ij` instead, so a pair with no path contributes `1 / inf = 0` and an
unconnected region takes the lowest attainable value rather than an undefined
one. This is the reason efficiency is used for cortical thickness networks
(He et al., 2009; Latora and Marchiori, 2001), and it keeps every region
averaged over the same `V - 1` others without substituting a distance.

Connectivity (mean degree, isolated regions, share of connected participants,
component count) is reported across a range of costs, in the spirit of
examining a cost range rather than a single threshold, and is printed for the
cost the features are built at.

## References

- Zhang, T. et al. (2021). Predicting MCI to AD conversion using integrated sMRI
  and rs-fMRI: machine learning and graph theory approach. *Frontiers in Aging
  Neuroscience*, 13, 688926.
- He, Y. et al. (2009). Impaired small-world efficiency in structural cortical
  networks in multiple sclerosis associated with white matter lesion load.
  *Brain*, 132, 3366-3379.
- Latora, V. and Marchiori, M. (2001). Efficient behavior of small-world
  networks. *Physical Review Letters*, 87, 198701.

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
examples/demo_cost_connectivity.csv
examples/demo_cv_classification_metrics.csv
examples/demo_cv_fold_metrics.csv
examples/demo_classification_metrics.csv
figures/group_mean_similarity_matrices.svg
figures/classification_performance.svg
figures/cv_classification_performance.svg
```

## Evaluation Outputs

The primary evaluation output is the stratified 5-fold cross-validation table:

```text
examples/demo_cv_classification_metrics.csv
```

The single train/test split table is kept as a quick demonstration of the pipeline:

```text
examples/demo_classification_metrics.csv
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
