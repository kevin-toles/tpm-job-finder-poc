from setuptools import setup, find_packages

setup(
    name="tpm-job-finder-poc",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "python-dotenv",
        "flask", 
        "pydantic",
        "openpyxl",
        "pytest",
        "pytest-asyncio",
        "aiohttp",
    ],
    python_requires=">=3.8",
)
