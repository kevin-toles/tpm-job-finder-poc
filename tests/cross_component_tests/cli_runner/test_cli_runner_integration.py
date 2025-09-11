import subprocess
import os
import sys
import tempfile
import pandas as pd

def test_cli_runner_end_to_end(tmp_path):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sample_jobs = os.path.join(base_dir, 'fixtures', 'remoteok_sample.json')
    sample_resume = os.path.join(base_dir, 'fixtures', 'sample_resume.txt')
    sample_applied = os.path.join(base_dir, 'fixtures', 'sample_applied.xlsx')
    output_path = str(tmp_path / 'output.xlsx')
    log_path = str(tmp_path / 'output.log')
    cmd = [
        sys.executable, '-m', 'tpm_job_finder_poc.cli_runner',
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
    env = os.environ.copy()
    env['PYTHONPATH'] = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    assert result.returncode == 0, f"CLI failed: {result.stderr}"
    assert os.path.exists(output_path), "Output file not created"
    df = pd.read_excel(output_path)
    assert not df.empty, "Output file is empty"
    os.remove(output_path)
    if os.path.exists(log_path):
        os.remove(log_path)
