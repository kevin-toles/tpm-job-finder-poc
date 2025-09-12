import subprocess
import os
import sys
import tempfile
import pandas as pd

def test_cli_runner_e2e_real_world(tmp_path):
    # Get the root project directory and use tests/cross_component_tests fixtures
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    fixtures_dir = os.path.join(project_root, 'tests', 'cross_component_tests', 'fixtures')
    sample_jobs = os.path.join(fixtures_dir, 'remoteok_sample.json')
    sample_resume = os.path.join(fixtures_dir, 'sample_resume.txt')
    sample_applied = os.path.join(fixtures_dir, 'sample_applied.xlsx')
    output_path = str(tmp_path / 'output.csv')
    log_path = str(tmp_path / 'output.log')
    # Use explicit project root path for PYTHONPATH
    cmd = [
        sys.executable, '-m', 'tpm_job_finder_poc.cli_runner',
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
    env['PYTHONPATH'] = project_root
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    print(f"Return code: {result.returncode}")
    print(f"STDOUT: {result.stdout}")
    print(f"STDERR: {result.stderr}")
    assert result.returncode == 0, f"CLI failed: {result.stderr}"
    assert os.path.exists(output_path), "Output file not created"
    df = pd.read_csv(output_path)
    assert not df.empty, "Output file is empty"
    os.remove(output_path)
    if os.path.exists(log_path):
        os.remove(log_path)
