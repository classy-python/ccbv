from setuptools import setup


setup(
    name="ccbv",
    version="0.1",
    packages=["ccbv"],
    install_requires=[
        "click",
        "colorama",
        "first",
        "jinja2-highlight",
        "more_itertools",
        "natsort",
        "requests",
        "six",
        "sphinx",
        "structlog",
        "virtualenv",
    ],
    entry_points={"console_scripts": ["ccbv=ccbv.cli:cli"]},
)
