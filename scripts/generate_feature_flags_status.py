#!/usr/bin/env python3
"""
Script to generate a dynamic markdown document listing all feature flags and their enabled/disabled status.
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.config import Config

FEATURE_FLAGS = {
    "Greenhouse Connector": "ENABLE_GREENHOUSE",
    "Lever Connector": "ENABLE_LEVER",
    "RemoteOK Connector": "ENABLE_REMOTEOK",
}

def get_flag_status(flag_name):
    return os.getenv(flag_name, "true").lower() == "true"

def main():
    lines = [
        "# Feature Flags Status\n",
        "| Component            | Feature Flag        | Enabled |\n",
        "|----------------------|---------------------|---------|\n",
    ]
    for component, flag in FEATURE_FLAGS.items():
        enabled = get_flag_status(flag)
        status = "✅ Enabled" if enabled else "❌ Disabled"
        lines.append(f"| {component:<20} | {flag:<19} | {status:<7} |\n")
    with open("FEATURE_FLAGS_STATUS.md", "w") as f:
        f.writelines(lines)
    print("FEATURE_FLAGS_STATUS.md updated.")

if __name__ == "__main__":
    main()
