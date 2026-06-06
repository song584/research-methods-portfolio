from __future__ import annotations

import numpy as np
import pandas as pd


def infer_regions(df: pd.DataFrame, suffix: str = "_thickness") -> list[str]:
    """Infer region names from columns such as ``lh_entorhinal_thickness``."""

    return [col[: -len(suffix)] for col in df.columns if col.endswith(suffix)]


def make_structural_feature_matrix(
    df: pd.DataFrame,
    regions: list[str] | None = None,
    modalities: tuple[str, ...] = ("thickness", "volume", "area"),
) -> tuple[np.ndarray, list[str]]:
    """Return subject-level structural features and corresponding column names."""

    if regions is None:
        regions = infer_regions(df)

    columns: list[str] = []
    for modality in modalities:
        columns.extend([f"{region}_{modality}" for region in regions])

    missing = [col for col in columns if col not in df.columns]
    if missing:
        raise ValueError(f"Missing structural columns: {missing[:5]}")

    return df[columns].to_numpy(dtype=float), columns


def _similarity_from_thickness(thickness: np.ndarray, alpha: float) -> np.ndarray:
    diff_squared = np.square(thickness[:, np.newaxis] - thickness[np.newaxis, :])
    matrix = np.exp(-diff_squared / alpha)
    np.fill_diagonal(matrix, 0.0)
    return matrix


def _threshold_by_cost(matrix: np.ndarray, cost: float) -> np.ndarray:
    if not 0 < cost < 1:
        raise ValueError("cost must be between 0 and 1")

    upper_values = matrix[np.triu_indices_from(matrix, k=1)]
    positive = upper_values[upper_values > 0]
    threshold = np.percentile(positive, 100 * (1 - cost))
    binary = (matrix > threshold).astype(int)
    np.fill_diagonal(binary, 0)
    return binary


def _shortest_paths_from(binary: np.ndarray, source: int) -> np.ndarray:
    """Compute unweighted shortest path lengths from one source node."""

    n_nodes = binary.shape[0]
    distances = np.full(n_nodes, np.inf)
    distances[source] = 0
    frontier = [source]

    while frontier:
        current = frontier.pop(0)
        neighbors = np.flatnonzero(binary[current])
        for neighbor in neighbors:
            if np.isinf(distances[neighbor]):
                distances[neighbor] = distances[current] + 1
                frontier.append(int(neighbor))

    return distances


def _node_path_lengths(binary: np.ndarray) -> list[float]:
    n_nodes = binary.shape[0]
    values: list[float] = []
    for node in range(n_nodes):
        distances = _shortest_paths_from(binary, source=node)
        finite = distances[np.isfinite(distances)]
        if len(finite) <= 1:
            values.append(0.0)
        else:
            values.append(float(np.mean(finite)))
    return values


def build_similarity_networks(
    df: pd.DataFrame,
    cost: float = 0.25,
    alpha: float = 0.01,
    regions: list[str] | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, list[str]]:
    """Build weighted and binary cortical-thickness similarity networks.

    Returns
    -------
    weighted_networks:
        Array with shape ``(n_subjects, n_regions, n_regions)``.
    binary_networks:
        Cost-thresholded binary networks with the same shape.
    network_features:
        Node-level mean shortest path length and degree, concatenated as
        ``[NL_region_1..N, ND_region_1..N]``.
    feature_names:
        Names for the network feature columns.
    """

    if regions is None:
        regions = infer_regions(df)

    thickness_columns = [f"{region}_thickness" for region in regions]
    thickness_values = df[thickness_columns].to_numpy(dtype=float)

    weighted_networks = []
    binary_networks = []
    network_features = []

    for thickness in thickness_values:
        weighted = _similarity_from_thickness(thickness, alpha=alpha)
        binary = _threshold_by_cost(weighted, cost=cost)
        node_lengths = _node_path_lengths(binary)
        node_degrees = binary.sum(axis=1).astype(float).tolist()

        weighted_networks.append(weighted)
        binary_networks.append(binary)
        network_features.append(node_lengths + node_degrees)

    feature_names = [f"{region}_NL" for region in regions] + [
        f"{region}_ND" for region in regions
    ]

    return (
        np.asarray(weighted_networks),
        np.asarray(binary_networks),
        np.asarray(network_features, dtype=float),
        feature_names,
    )


def build_feature_sets(
    df: pd.DataFrame,
    cost: float = 0.25,
    alpha: float = 0.01,
    regions: list[str] | None = None,
) -> dict[str, object]:
    """Build structural, network, and combined feature matrices."""

    if regions is None:
        regions = infer_regions(df)

    structural_features, structural_names = make_structural_feature_matrix(df, regions)
    weighted, binary, network_features, network_names = build_similarity_networks(
        df, cost=cost, alpha=alpha, regions=regions
    )
    all_features = np.hstack([structural_features, network_features])

    return {
        "regions": regions,
        "structural_features": structural_features,
        "structural_feature_names": structural_names,
        "weighted_networks": weighted,
        "binary_networks": binary,
        "network_features": network_features,
        "network_feature_names": network_names,
        "all_features": all_features,
        "all_feature_names": structural_names + network_names,
    }
