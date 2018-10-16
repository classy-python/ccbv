from setuptools import setup


setup(
    name="ccbv",
    version="0.1",
    packages=["ccbv"],
    install_requires=[
        "click",
        "colorama",
        "jinja2-highlight",
        "six",
        "structlog",
        "virtualenv",
    ],
    entry_points={"console_scripts": ["ccbv=ccbv.cli:cli"]},
)
