from setuptools import setup

setup(
    name="trading_cw_trigger",
    version="1.0.0",
    packages=["dto", "utils", "tda_api", "strategies", "dto.factories"],
    python_requires=">=3.7",
    install_requires=[
        "tda-api>=1.5.2",
        "yfinance>=0.1.70",
        "numpy>=1.22.3",
        "pytz>=2021.3",
        "watchtower>=3.0.0",
    ],
    package_dir={"": "src"},
    url="",
    license="CC BY-NC-ND 4.0",
    author="Tyler Roberts",
    author_email="tjroberts314@gmail.com",
    description="AWS Lambda triggered trading startegies for TDA",
)
