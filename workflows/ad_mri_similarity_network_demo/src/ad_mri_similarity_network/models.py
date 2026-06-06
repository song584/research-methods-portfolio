from __future__ import annotations

import numpy as np


def _stratified_split(
    X: np.ndarray,
    y: np.ndarray,
    test_size: float,
    random_state: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(random_state)
    train_indices = []
    test_indices = []
    for label in np.unique(y):
        label_indices = np.flatnonzero(y == label)
        rng.shuffle(label_indices)
        n_test = max(1, int(round(len(label_indices) * test_size)))
        test_indices.extend(label_indices[:n_test])
        train_indices.extend(label_indices[n_test:])

    train_indices = np.asarray(train_indices)
    test_indices = np.asarray(test_indices)
    rng.shuffle(train_indices)
    rng.shuffle(test_indices)
    return X[train_indices], X[test_indices], y[train_indices], y[test_indices]


def _stratified_kfold_indices(
    y: np.ndarray,
    n_splits: int,
    random_state: int,
) -> list[tuple[np.ndarray, np.ndarray]]:
    if n_splits < 2:
        raise ValueError("n_splits must be at least 2")

    rng = np.random.default_rng(random_state)
    folds = [[] for _ in range(n_splits)]
    all_indices = np.arange(len(y))

    for label in np.unique(y):
        label_indices = np.flatnonzero(y == label)
        rng.shuffle(label_indices)
        for i, idx in enumerate(label_indices):
            folds[i % n_splits].append(int(idx))

    splits = []
    for fold in folds:
        test_idx = np.asarray(sorted(fold), dtype=int)
        train_idx = np.setdiff1d(all_indices, test_idx)
        splits.append((train_idx, test_idx))
    return splits


def _standardize_train_test(
    X_train: np.ndarray,
    X_test: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    mean = X_train.mean(axis=0)
    scale = X_train.std(axis=0)
    scale[scale == 0] = 1.0
    return (X_train - mean) / scale, (X_test - mean) / scale


def _sigmoid(z: np.ndarray) -> np.ndarray:
    z = np.clip(z, -40, 40)
    return 1.0 / (1.0 + np.exp(-z))


def _fit_logistic_regression(
    X: np.ndarray,
    y: np.ndarray,
    learning_rate: float = 0.05,
    n_iter: int = 2500,
    l2: float = 0.01,
) -> np.ndarray:
    X_aug = np.c_[np.ones(len(X)), X]
    weights = np.zeros(X_aug.shape[1])

    class_counts = np.bincount(y.astype(int), minlength=2)
    class_weights = {
        0: len(y) / max(1, 2 * class_counts[0]),
        1: len(y) / max(1, 2 * class_counts[1]),
    }
    sample_weights = np.asarray([class_weights[int(label)] for label in y])

    for _ in range(n_iter):
        prob = _sigmoid(X_aug @ weights)
        error = (prob - y) * sample_weights
        grad = (X_aug.T @ error) / len(y)
        grad[1:] += l2 * weights[1:]
        weights -= learning_rate * grad

    return weights


def _predict_logistic(X: np.ndarray, weights: np.ndarray) -> np.ndarray:
    return _sigmoid(np.c_[np.ones(len(X)), X] @ weights)


def _predict_nearest_centroid(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_test: np.ndarray,
) -> np.ndarray:
    c0 = X_train[y_train == 0].mean(axis=0)
    c1 = X_train[y_train == 1].mean(axis=0)
    d0 = np.linalg.norm(X_test - c0, axis=1)
    d1 = np.linalg.norm(X_test - c1, axis=1)
    # Convert distance difference to a probability-like score.
    return _sigmoid(d0 - d1)


def _auc_score(y_true: np.ndarray, score: np.ndarray) -> float:
    y_true = y_true.astype(int)
    n_pos = int(y_true.sum())
    n_neg = int(len(y_true) - n_pos)
    if n_pos == 0 or n_neg == 0:
        return float("nan")

    order = np.argsort(score)
    ranks = np.empty_like(order, dtype=float)
    ranks[order] = np.arange(1, len(score) + 1)
    rank_sum_pos = ranks[y_true == 1].sum()
    return float((rank_sum_pos - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg))


def _metrics(y_true: np.ndarray, y_pred: np.ndarray, y_prob: np.ndarray) -> dict[str, float | list[list[int]]]:
    tp = int(np.sum((y_true == 1) & (y_pred == 1)))
    tn = int(np.sum((y_true == 0) & (y_pred == 0)))
    fp = int(np.sum((y_true == 0) & (y_pred == 1)))
    fn = int(np.sum((y_true == 1) & (y_pred == 0)))

    accuracy = (tp + tn) / max(1, len(y_true))
    sensitivity = tp / max(1, tp + fn)
    specificity = tn / max(1, tn + fp)
    precision = tp / max(1, tp + fp)
    f1 = 2 * precision * sensitivity / max(1e-12, precision + sensitivity)

    return {
        "accuracy": float(accuracy),
        "sensitivity": float(sensitivity),
        "specificity": float(specificity),
        "auc": _auc_score(y_true, y_prob),
        "f1": float(f1),
        "confusion_matrix": [[tn, fp], [fn, tp]],
    }


def evaluate_binary_classifier(
    X: np.ndarray,
    y: np.ndarray,
    model: str = "logistic",
    positive_label: int = 3,
    test_size: float = 0.2,
    random_state: int = 42,
) -> dict[str, float | str | list[list[int]]]:
    """Fit a simple binary classifier and return common diagnostic metrics.

    The implementation intentionally avoids heavy dependencies so the demo can
    run in a minimal Python environment.
    """

    X = np.asarray(X, dtype=float)
    y_binary = np.where(y == positive_label, 1, 0)
    X_train, X_test, y_train, y_test = _stratified_split(
        X,
        y_binary,
        test_size=test_size,
        random_state=random_state,
    )
    X_train, X_test = _standardize_train_test(X_train, X_test)

    if model == "logistic":
        weights = _fit_logistic_regression(X_train, y_train)
        y_prob = _predict_logistic(X_test, weights)
    elif model == "centroid":
        y_prob = _predict_nearest_centroid(X_train, y_train, X_test)
    else:
        raise ValueError("model must be 'logistic' or 'centroid'")

    y_pred = (y_prob >= 0.5).astype(int)
    out = _metrics(y_test, y_pred, y_prob)
    out["model"] = model
    return out


def evaluate_binary_classifier_cv(
    X: np.ndarray,
    y: np.ndarray,
    model: str = "logistic",
    positive_label: int = 3,
    n_splits: int = 5,
    random_state: int = 42,
) -> dict[str, object]:
    """Evaluate a binary classifier with stratified k-fold cross-validation."""

    X = np.asarray(X, dtype=float)
    y_binary = np.where(y == positive_label, 1, 0)
    fold_rows = []

    for fold_id, (train_idx, test_idx) in enumerate(
        _stratified_kfold_indices(y_binary, n_splits=n_splits, random_state=random_state),
        start=1,
    ):
        X_train, X_test = _standardize_train_test(X[train_idx], X[test_idx])
        y_train = y_binary[train_idx]
        y_test = y_binary[test_idx]

        if model == "logistic":
            weights = _fit_logistic_regression(X_train, y_train)
            y_prob = _predict_logistic(X_test, weights)
        elif model == "centroid":
            y_prob = _predict_nearest_centroid(X_train, y_train, X_test)
        else:
            raise ValueError("model must be 'logistic' or 'centroid'")

        y_pred = (y_prob >= 0.5).astype(int)
        metrics = _metrics(y_test, y_pred, y_prob)
        metrics["fold"] = fold_id
        metrics["model"] = model
        fold_rows.append(metrics)

    metric_names = ["accuracy", "sensitivity", "specificity", "auc", "f1"]
    summary: dict[str, object] = {
        "model": model,
        "n_splits": n_splits,
        "folds": fold_rows,
    }
    for metric in metric_names:
        values = np.asarray([float(row[metric]) for row in fold_rows])
        summary[f"{metric}_mean"] = float(np.nanmean(values))
        summary[f"{metric}_std"] = float(np.nanstd(values, ddof=1))
    return summary
