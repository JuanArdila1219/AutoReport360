"""Shared descriptive checks for validation and data profiling."""
import pandas as pd


def iqr_outlier_count(values: pd.Series) -> int:
    """Count observations outside the conventional 1.5-IQR fences."""
    q1, q3 = values.quantile([0.25, 0.75])
    spread = q3 - q1
    return int(((values < q1 - 1.5 * spread) | (values > q3 + 1.5 * spread)).sum())
