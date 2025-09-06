"""
Lightweight smoke integration: run all three connectors offline via fixtures.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import json
import importlib.resources as pkg

from poc.aggregators.greenhouse import GreenhouseConnector
from poc.aggregators.lever import LeverConnector
from poc.aggregators.remoteok import RemoteOKConnector


def _load(path: Path) -> Any:
    return json.loads(path.read_text())


def test_all_connectors_offline(tmp_path: Path) -> None:
    """Uses local fixture files (monkey-patched) so no network hit."""
    # remoteok -----------------------------------------------------------------
    import requests
    from tests.aggregators.conftest import fixtures_dir

    with (fixtures_dir() / "remoteok_sample.json").open() as fh:
        payload = fh.read()

    def _mock_get(*_: Any, **__: Any):  # noqa: D401
        resp = requests.Response()
        resp.status_code = 200
        resp._content = payload.encode()  # type: ignore[attr-defined]
        return resp

    requests.get = _mock_get  # type: ignore[assignment]
    assert RemoteOKConnector().fetch_since()

    # greenhouse / lever just ensure class instantiation works
    assert GreenhouseConnector(companies=["example"]).companies
    assert LeverConnector(companies=["example"]).companies"""
Lightweight smoke integration: run all three connectors offline via fixtures.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import json
import importlib.resources as pkg

from poc.aggregators.greenhouse import GreenhouseConnector
from poc.aggregators.lever import LeverConnector
from poc.aggregators.remoteok import RemoteOKConnector


def _load(path: Path) -> Any:
    return json.loads(path.read_text())


def test_all_connectors_offline(tmp_path: Path) -> None:
    """Uses local fixture files (monkey-patched) so no network hit."""
    # remoteok -----------------------------------------------------------------
    import requests
    from tests.aggregators.conftest import fixtures_dir

    with (fixtures_dir() / "remoteok_sample.json").open() as fh:
        payload = fh.read()

    def _mock_get(*_: Any, **__: Any):  # noqa: D401
        resp = requests.Response()
        resp.status_code = 200
        resp._content = payload.encode()  # type: ignore[attr-defined]
        return resp

    requests.get = _mock_get  # type: ignore[assignment]
    assert RemoteOKConnector().fetch_since()

    # greenhouse / lever just ensure class instantiation works
    assert GreenhouseConnector(companies=["example"]).companies
    assert LeverConnector(companies=["example"]).companies
