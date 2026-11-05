
import sys
from pathlib import Path

import pandas as pd
import pytest

# Add the causal_ml directory to Python's import path.
CAUSAL_ML_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CAUSAL_ML_DIR))

from heterogeneous_treatment_effects import create_price_segments


def test_price_segments_create_three_groups():
    prices = pd.Series(range(1, 10))

    result = create_price_segments(prices)

    assert len(result) == 9
    assert set(result.astype(str)) == {"Low", "Medium", "High"}


def test_price_segments_have_no_missing_values():
    prices = pd.Series([100, 200, 300, 400, 500, 600])

    result = create_price_segments(prices)

    assert result.isna().sum() == 0


def test_price_segments_preserve_input_length():
    prices = pd.Series(range(1, 101))

    result = create_price_segments(prices)

    assert len(result) == len(prices)


def test_price_segments_reject_empty_input():
    prices = pd.Series([], dtype=float)

    with pytest.raises(ValueError):
        create_price_segments(prices)
