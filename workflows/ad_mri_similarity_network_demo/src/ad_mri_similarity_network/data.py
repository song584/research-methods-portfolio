from __future__ import annotations

import numpy as np
import pandas as pd


def generate_synthetic_structural_data(
    n_controls: int = 90,
    n_ad: int = 90,
    random_state: int = 42,
) -> pd.DataFrame:
    """Create a synthetic FreeSurfer-like regional structural MRI table.

    Values are made up. They follow the column layout the pipeline expects —
    regional thickness, volume, and surface area plus a diagnosis label — with
    a temporal-lobe effect in the AD group.
    """

    rng = np.random.default_rng(random_state)
    structures = (
        "bankssts",
        "caudalanteriorcingulate",
        "caudalmiddlefrontal",
        "cuneus",
        "entorhinal",
        "fusiform",
        "inferiorparietal",
        "inferiortemporal",
        "isthmuscingulate",
        "lateraloccipital",
        "lateralorbitofrontal",
        "lingual",
        "medialorbitofrontal",
        "middletemporal",
        "parahippocampal",
        "paracentral",
        "parsopercularis",
        "parsorbitalis",
        "parstriangularis",
        "pericalcarine",
        "postcentral",
        "posteriorcingulate",
        "precentral",
        "precuneus",
        "rostralanteriorcingulate",
        "rostralmiddlefrontal",
        "superiorfrontal",
        "superiorparietal",
        "superiortemporal",
        "supramarginal",
        "frontalpole",
        "temporalpole",
        "transversetemporal",
        "insula",
    )
    regions = [f"{hemi}_{name}" for hemi in ("lh", "rh") for name in structures]

    rows = []
    for group_label, n_group in [(0, n_controls), (3, n_ad)]:
        for i in range(n_group):
            row: dict[str, float | int | str] = {
                "subject_id": f"sub-{group_label}-{i:03d}",
                "diagnosis": group_label,
            }
            for region in regions:
                is_temporal = "entorhinal" in region or "inferiortemporal" in region
                thickness_shift = -0.35 if group_label == 3 and is_temporal else 0.0
                volume_shift = -0.22 if group_label == 3 and is_temporal else 0.0
                area_shift = -0.10 if group_label == 3 and is_temporal else 0.0

                row[f"{region}_thickness"] = rng.normal(2.55 + thickness_shift, 0.18)
                row[f"{region}_volume"] = rng.normal(3.50 + volume_shift, 0.28)
                row[f"{region}_area"] = rng.normal(1.70 + area_shift, 0.15)
            rows.append(row)

    return pd.DataFrame(rows)

