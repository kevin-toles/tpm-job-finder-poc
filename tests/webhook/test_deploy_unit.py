from src.webhook.deploy import VersionRegistry, authenticate_request, notify_admin, cloud_deploy_hook

def test_version_registry_log(tmp_path):
    reg = VersionRegistry(str(tmp_path / "registry.txt"))
    reg.log("roll-forward", "v1.2.3", "admin")
    with open(tmp_path / "registry.txt") as f:
        lines = f.readlines()
    assert "roll-forward to version v1.2.3 by admin" in lines[0]

def test_authenticate_request_stub():
    class DummyReq: pass
    assert authenticate_request(DummyReq()) is True

def test_notify_admin_stub(capsys):
    notify_admin("Test message")
    captured = capsys.readouterr()
    assert "[ADMIN NOTIFY] Test message" in captured.out

def test_cloud_deploy_hook_stub(capsys):
    cloud_deploy_hook("roll-forward", "v1.2.3")
    captured = capsys.readouterr()
    assert "[CLOUD HOOK] roll-forward v1.2.3" in captured.out
