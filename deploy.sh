#!/bin/bash

# Step 1: Make changes to your code
# This step is manual and not included in this script

# Step 2: Update the version number in setup.py and pyproject.toml
# This step is manual and not included in this script
# remember to update the pyproject.toml file as well

# Step 3: Rebuild your package
# Remember to delete the old distribution files in the dist/ directory before running the python setup.py sdist bdist_wheel command to avoid uploading old packages to PyPI
rm -r dist/*
rm *.drawio
rm -r build/lib/*
python setup.py sdist bdist_wheel

# Step 4: Commit your changes to your local Git repository
git add .
git commit -m "Update package to version 0.6.7" # Replace "x.y.z" with your new version number. Remember to update setup.py and pyproject.toml before running this command

git tag -a v0.6.7 -m "Update package to version 0.6.7" # Replace "x.y.z" with your new version number. Remember to update setup.py and pyproject.toml before running this command
# Step 5: Push your changes to GitHub
git push origin main # Replace "main" with the name of your branch if it's different
