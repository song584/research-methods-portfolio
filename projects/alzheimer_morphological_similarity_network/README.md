# Alzheimer's Disease Morphological Similarity Network

## Project Summary

This project explored whether structural MRI-derived regional morphometric features and subject-level similarity-network features could support Alzheimer's disease and MCI-related classification tasks.

## My Role

- Organized and explored a large multimodal AD/MCI dataset.
- Checked subject identifiers, duplicate records, diagnosis labels, APOE, amyloid PET, MRI availability, and cognitive test availability.
- Implemented cortical-thickness similarity network construction from regional structural MRI features.
- Extracted graph-theory features such as node-level path length and degree.
- Compared structural, network, and combined feature sets in machine-learning classifiers.
- Explored SVM, logistic regression, random forest, SHAP, and early GCN/GAT graph-classification variants.
- Prepared analysis outputs for poster/project reporting.

## Methods Used

- Structural MRI feature engineering
- Cortical similarity network construction
- Cost-based network thresholding
- Graph feature extraction with NetworkX
- SVM/logistic regression/random forest classification
- SHAP-based model interpretation attempts
- Exploratory PyTorch Geometric GCN/GAT modeling

## Related Workflow Demo

The public demo below reflects the type of analysis workflow used in this project with synthetic data:

```text
../../workflows/ad_mri_similarity_network_demo/
```

The workflow demo is not the original study code or dataset. It is a cleaned, public-safe implementation of the core analysis logic.

