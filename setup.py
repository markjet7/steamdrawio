from setuptools import setup, find_packages

setup(
    name="steamdrawio",
    version="0.1",
    author="Mark Mba Wright",
    author_email="markmw@iastate.edu",
    packages=find_packages(),
    package_dir={"steamdrawio": "src/steamdrawio"},
    package_data={"steamdrawio": ["src/steamdrawio/shapes.csv"]},
    install_requires=[
        "networkx"
    ],
)
