# =============================================================================
# Shared Python Package — Emergency Edge/Fog Communication System
# =============================================================================
from setuptools import setup, find_packages

setup(
    name="emergency-shared",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "pydantic>=2.0",
        "pydantic-settings>=2.0",
    ],
    python_requires=">=3.11",
)
