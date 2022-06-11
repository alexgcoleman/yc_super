from setuptools import setup, find_packages

setup(
    name='yc_super',
    packages=find_packages(),
    python_requires='>=3.10', # TODO: check compatibility with 3.9
    install_requires=[
        "pandas",
        "openpyxl"
    ]
)