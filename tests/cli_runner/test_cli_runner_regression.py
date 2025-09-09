import pytest
from src.cli_runner.main import CLIRunner
import pandas as pd

def test_export_results_unsupported_format(tmp_path):
    runner = CLIRunner()
    df = pd.DataFrame({"JobID": [1], "score": [0.9]})
    out = tmp_path / "out.unsupported"
    with pytest.raises(ValueError):
        runner._export_results(df, str(out), "unsupported")
