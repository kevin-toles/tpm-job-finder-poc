import requests
import json
import os

def save_fixture(data, filename):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

def fetch_remoteok():
    url = "https://remoteok.com/api"
    resp = requests.get(url)
    resp.raise_for_status()
    jobs = resp.json()
    save_fixture(jobs, "cross_component_tests/fixtures/remoteok_sample.json")

def fetch_greenhouse():
    # Example: Greenhouse public jobs endpoint for a company
    company = "example-company"  # Replace with real company
    url = f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs"
    resp = requests.get(url)
    resp.raise_for_status()
    jobs = resp.json()
    save_fixture(jobs, "cross_component_tests/fixtures/greenhouse_sample.json")

def fetch_lever():
    # Example: Lever public jobs endpoint for a company
    company = "example-company"  # Replace with real company
    url = f"https://api.lever.co/v1/postings/{company}?mode=json"
    resp = requests.get(url)
    resp.raise_for_status()
    jobs = resp.json()
    save_fixture(jobs, "cross_component_tests/fixtures/lever_sample.json")

def main():
    print("Fetching RemoteOK sample...")
    fetch_remoteok()
    print("Fetching Greenhouse sample...")
    fetch_greenhouse()
    print("Fetching Lever sample...")
    fetch_lever()
    print("Done.")

if __name__ == "__main__":
    main()
