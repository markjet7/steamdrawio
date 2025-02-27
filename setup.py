from setuptools import setup

setup(
    name="steamdrawio",
    version="0.6.7",
    author="Mark Mba Wright",
    author_email="markmw@iastate.edu",
    packages=["steamdrawio"],
    package_dir={"steamdrawio": "src/steamdrawio"},
    package_data={"steamdrawio": ["src/steamdrawio/shapes.csv"]},
    install_requires=["igraph"],
)
