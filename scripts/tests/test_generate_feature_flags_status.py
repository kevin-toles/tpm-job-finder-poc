import os
import sys
import tempfile
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from scripts.generate_feature_flags_status import FEATURE_FLAGS, main as generate_status

def test_feature_flags_status_file(tmp_path, monkeypatch):
    # Monkeypatch feature flags to test enabled/disabled
    monkeypatch.setenv("ENABLE_GREENHOUSE", "false")
    monkeypatch.setenv("ENABLE_LEVER", "true")
    monkeypatch.setenv("ENABLE_REMOTEOK", "false")
    # Change working directory to tmp_path
    os.chdir(tmp_path)
    # Generate the status file
    generate_status()
    # Check file exists
    status_file = tmp_path / "FEATURE_FLAGS_STATUS.md"
    assert status_file.exists()
    content = status_file.read_text()
    assert "Greenhouse Connector" in content
    assert "❌ Disabled" in content
    assert "✅ Enabled" in content
    assert "RemoteOK Connector" in content

@pytest.mark.integration
def test_status_file_updates_on_flag_change(tmp_path, monkeypatch):
    monkeypatch.setenv("ENABLE_GREENHOUSE", "true")
    os.chdir(tmp_path)
    generate_status()
    content = (tmp_path / "FEATURE_FLAGS_STATUS.md").read_text()
    assert "✅ Enabled" in content
    monkeypatch.setenv("ENABLE_GREENHOUSE", "false")
    generate_status()
    content = (tmp_path / "FEATURE_FLAGS_STATUS.md").read_text()
    assert "❌ Disabled" in content
