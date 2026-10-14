import sys
import warnings
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))  # works without `pip install`

import matplotlib.pyplot as plt  # noqa: E402
import pytest  # noqa: E402


@pytest.fixture(autouse=True)
def _close_figures():
    yield
    plt.close("all")
    matplotlib.rcdefaults()


@pytest.fixture
def sp():
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        import sciplot
    return sciplot
