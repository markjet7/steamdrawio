# Installation
This package draws a horizontal flowchart of a biosteam model using the NetworkX package.
To use this package, first, install graphviz and pygraphviz/

Instructions to install graphviz: https://graphviz.gitlab.io/download/

Instructions to install pygraphviz: https://pygraphviz.github.io/documentation/stable/install.html
    
Then install the steamdrawio package using pip:
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
