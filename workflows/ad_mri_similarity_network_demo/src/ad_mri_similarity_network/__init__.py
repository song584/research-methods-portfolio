"""Utilities for structural MRI similarity-network demos."""

from .data import generate_synthetic_structural_data
from .features import (
    build_feature_sets,
    build_similarity_networks,
    infer_regions,
    make_structural_feature_matrix,
)
from .models import evaluate_binary_classifier, evaluate_binary_classifier_cv

__all__ = [
    "build_feature_sets",
    "build_similarity_networks",
    "evaluate_binary_classifier",
    "evaluate_binary_classifier_cv",
    "generate_synthetic_structural_data",
    "infer_regions",
    "make_structural_feature_matrix",
]
