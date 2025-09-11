from __future__ import annotations
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any
import json
from tpm_job_finder_poc.job_aggregator.aggregators.greenhouse import GreenhouseConnector
from tpm_job_finder_poc.job_aggregator.aggregators.lever import LeverConnector
from tpm_job_finder_poc.job_aggregator.aggregators.remoteok import RemoteOKConnector

"""
Lightweight smoke integration: run all three connectors offline via fixtures.
"""

def _load(path: Path) -> Any:
    return json.loads(path.read_text())

def test_all_connectors_offline(tmp_path: Path, monkeypatch) -> None:
    from tpm_job_finder_poc.config.config import config
    import pytest
    import os
    # Calculate fixtures directory
    current_dir = Path(__file__).parent
    project_root = current_dir.parent.parent.parent
    fixtures_dir = project_root / "cross_component_tests" / "fixtures"
    
    if not config.ENABLE_REMOTEOK:
        pytest.skip("RemoteOK connector is disabled by feature flag")
    if not config.ENABLE_GREENHOUSE:
        pytest.skip("Greenhouse connector is disabled by feature flag")
    if not config.ENABLE_LEVER:
        pytest.skip("Lever connector is disabled by feature flag")
    """Uses local fixture files (monkey-patched) so no network hit."""
    # remoteok -----------------------------------------------------------------
    import requests
    import json

    sample = json.loads((fixtures_dir / "remoteok_sample.json").read_text(encoding="utf-8"))
    # make sure at least one record is < 7 days old
    sample[0]["epoch"] = int((datetime.now(timezone.utc) - timedelta(hours=2)).timestamp())

    resp = requests.Response()
    resp.status_code = 200
    resp._content = json.dumps(sample).encode()
    monkeypatch.setattr("requests.get", lambda *args, **kwargs: resp)

    assert RemoteOKConnector().fetch_since(days=7)

    # greenhouse / lever just ensure class instantiation works
    assert GreenhouseConnector(companies=["example"]).companies
    assert LeverConnector(companies=["example"]).companies
