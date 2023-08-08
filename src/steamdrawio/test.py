# %%
from ethanol_tutorial import sys 
from steamdrawio import *
# %%
# %%
import networkx as nx
layout = ComputeHorizontalLayout(sys, 0, 0, 0, 0)
layout
# %%

draw(sys)
# %%
