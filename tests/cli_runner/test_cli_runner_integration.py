import subprocess
import os
import sys
import tempfile
import pandas as pd

def test_cli_runner_end_to_end():
    sample_jobs = os.path.join('tests', 'fixtures', 'remoteok_sample.json')
    sample_resume = os.path.join('tests', 'fixtures', 'sample_resume.txt')
    sample_applied = os.path.join('tests', 'fixtures', 'sample_applied.xlsx')
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as out:
        output_path = out.name
    log_path = output_path + '.log'
    cmd = [
        sys.executable, 'src/cli_runner/main.py',
        '--input', sample_jobs,
        '--resume', sample_resume,
        '--applied', sample_applied,
        '--output', output_path,
        '--log', log_path,
        '--export-format', 'excel',
        '--dedupe',
        '--enrich',
        '--verbose'
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0, f"CLI failed: {result.stderr}"
    assert os.path.exists(output_path), "Output file not created"
    df = pd.read_excel(output_path)
    assert not df.empty, "Output file is empty"
    os.remove(output_path)
    if os.path.exists(log_path):
        os.remove(log_path)
