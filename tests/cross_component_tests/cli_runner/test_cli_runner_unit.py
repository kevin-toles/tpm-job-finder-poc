import pytest
import sys
from tpm_job_finder_poc.cli_runner.main import CLIRunner

class DummyArgs:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

@pytest.mark.parametrize("missing_arg", ["input", "resume", "applied"])
def test_validate_args_missing_file(tmp_path, missing_arg):
    args = DummyArgs(input=tmp_path / "input.csv", resume=tmp_path / "resume.txt", applied=tmp_path / "applied.xlsx", output="out.xlsx")
    setattr(args, missing_arg, "nonexistent.file")
    runner = CLIRunner()
    with pytest.raises(FileNotFoundError):
        runner._validate_args(args)

def test_export_results_csv(tmp_path):
    import pandas as pd
    runner = CLIRunner()
    df = pd.DataFrame({"JobID": [1, 2], "score": [0.9, 0.8]})
    out = tmp_path / "out.csv"
    runner._export_results(df, str(out), "csv")
    loaded = pd.read_csv(out)
    assert list(loaded["JobID"]) == [1, 2]

def test_export_results_excel(tmp_path):
    import pandas as pd
    runner = CLIRunner()
    df = pd.DataFrame({"JobID": [1, 2], "score": [0.9, 0.8]})
    out = tmp_path / "out.xlsx"
    runner._export_results(df, str(out), "excel")
    loaded = pd.read_excel(out)
    assert list(loaded["JobID"]) == [1, 2]

def test_export_results_json(tmp_path):
    import pandas as pd
    runner = CLIRunner()
    df = pd.DataFrame({"JobID": [1, 2], "score": [0.9, 0.8]})
    out = tmp_path / "out.json"
    runner._export_results(df, str(out), "json")
    loaded = pd.read_json(out)
    assert set(loaded["JobID"]) == {1, 2}
