# Installation
This package draws a horizontal flowchart of a biosteam model using the igraph package.

Install Git: https://git-scm.com/downloads
Install the steamdrawio package using pip:
```
pip install git+https://github.com/markjet7/steamdrawio/ --upgrade
```
# Usage 
Then import it using:
```python
from steamdrawio import draw

# Then use the draw function to draw a biosteam model:
draw(model)
```

This will create a drawio file in the current working directory.
You can open the drawio file using the drawio desktop app or the draw.io website.

# Options
```python
draw(model, filename="your_filename") # Specify the filename

def label(stream):
    return f"{stream.ID}\n(Mass Flow: {stream.F_mass} kg/hr)" # Custom function to label streams
draw(model, filename="your_filename", label_fn=label) # Specify a custom function to label streams
```
