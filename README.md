# Installation
This package draws a horizontal flowchart of a biosteam model using the Networkx package.
To use this package, first install it using:
pip install https://github.com/markjet7/steamdrawio/blob/4022d5458023d00757b886a8cb6012da395b5a66/dist/steamdrawio-0.1.tar.gz
# Usage 
Then import it using:
from steamdrawio import draw
Then use the draw function to draw a biosteam model:
draw(model)

This will create a drawio file in the current working directory.
You can open the drawio file using the drawio desktop app or the draw.io website.
