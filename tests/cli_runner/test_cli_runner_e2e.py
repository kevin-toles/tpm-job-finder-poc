import subprocess
import os
import sys
import tempfile
import pandas as pd

def test_cli_runner_e2e_real_world():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sample_jobs = os.path.join(base_dir, 'tests', 'fixtures', 'remoteok_sample.json')
    sample_resume = os.path.join(base_dir, 'tests', 'fixtures', 'sample_resume.txt')
    sample_applied = os.path.join(base_dir, 'tests', 'fixtures', 'sample_applied.xlsx')
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as out:
        output_path = out.name
    log_path = output_path + '.log'
    cmd = [
        sys.executable, '-m', 'tpm_job_finder_poc.cli_runner.main',
        '--input', sample_jobs,
        '--resume', sample_resume,
        '--applied', sample_applied,
        '--output', output_path,
        '--log', log_path,
        '--export-format', 'csv',
        '--dedupe',
        '--enrich',
        '--verbose'
    ]
    env = os.environ.copy()
    env['PYTHONPATH'] = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    assert result.returncode == 0, f"CLI failed: {result.stderr}"
    assert os.path.exists(output_path), "Output file not created"
    df = pd.read_csv(output_path)
    assert not df.empty, "Output file is empty"
    os.remove(output_path)
    if os.path.exists(log_path):
        os.remove(log_path)
