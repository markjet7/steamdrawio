# Installation
This package draws a horizontal flowchart of a biosteam model using the igraph package.
   
Install the steamdrawio package using pip:
```
pip install git+https://github.com/markjet7/steamdrawio/ 
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
