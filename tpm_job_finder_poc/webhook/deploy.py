
# Stubs for test compatibility
class VersionRegistry:
    def __init__(self, path="version_registry.txt"):
        self.path = path
    def log(self, action, version, user):
        with open(self.path, "a") as f:
            f.write(f"{action} to version {version} by {user}\n")

def authenticate_request(req):
    return True

def notify_admin(msg):
    print(f"[ADMIN NOTIFY] {msg}")

def cloud_deploy_hook(action, version):
    print(f"[CLOUD HOOK] {action} {version}")

from .app import app
