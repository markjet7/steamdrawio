# %%
import pprint
import xml.etree.ElementTree as ET
import random
import importlib

import igraph as ig

# from layout_nodes import *

# %%

shapes = {
    "unit": ["process", "140", "100"],
    "mixer": ["mxgraph.pid.mixers.in-line_static_mixer", "70", "20"],
    "pump": ["mxgraph.pid.pumps.centrifugal_pump_1", "70", "70"],
    "steammixer": ["mxgraph.pid.piping.in-line_mixer", "100", "100"],
    "mockmixer": ["mxgraph.pid.piping.in-line_mixer", "60", "20"],
    "splitter": ["mxgraph.pid.filters.filter", "30", "30"],
    "phasesplitter": ["mxgraph.pid.separators.separator_(cyclone)2", "100", "100"],
    "mocksplitter": ["mxgraph.pid.filters.filter", "80", "120"],
    "reversedsplitter": ["mxgraph.pid.filters.filter", "30", "30"],
    "molecularsieve": [
        "mxgraph.pid.misc.screening_device,_sieve,_strainer",
        "100",
        "50",
    ],
    "hx": [
        "mxgraph.pid.heat_exchangers.fixed_straight_tubes_heat_exchanger",
        "50",
        "10",
    ],
    "hxutility": ["mxgraph.pid.heat_exchangers.heater", "60", "60"],
    "hxprocess": ["mxgraph.pid.heat_exchangers.condenser", "60", "60"],
    "tank": ["mxgraph.pid.vessels.tank_(dished_roof)", "150", "120"],
    "mixtank": ["mxgraph.pid.vessels.jacketed_mixing_vessel", "150", "200"],
    "storagetank": ["mxgraph.pid.vessels.tank_(floating_roof)", "160", "200"],
    "distillation": ["mxgraph.pid.vessels.tower_with_packing", "160", "200"],
    "binarydistillation": ["mxgraph.pid.vessels.tower_with_packing", "80", "220"],
    "shortcutcolumn": ["mxgraph.pid.vessels.tower_with_packing", "80", "220"],
    "duplicator": ["process", "100", "100"],
    "junction": ["process", "100", "140"],
    "massbalance": ["process", "100", "140"],
    "diagramonlyunit": ["process", "80", "80"],
    "diagramonlysystemunit": ["process", "80", "80"],
    "diagramonlystreamunit": ["process", "100", "40"],
    "flash": ["mxgraph.pid.separators.spray_scrubber", "100", "100"],
    "splitflash": ["mxgraph.pid.separators.spray_scrubber", "70", "67"],
    "ratioflash": ["mxgraph.pid.separators.spray_scrubber", "110", "60"],
    "multieffectevaporator": ["mxgraph.pid.heat_exchangers.condenser", "100", "95"],
    "solidsseparator": [
        "mxgraph.pid.separators.separator_(electromagnetic)",
        "14",
        "97",
    ],
    "rotaryvacuumfilter": ["mxgraph.pid.filters.press_filter", "52", "95"],
    "crushingmill": ["mxgraph.pid.crushers_grinding.crusher_(hammer)", "150", "80"],
    "hammermill": ["mxgraph.pid.crushers_grinding.crusher_(hammer)", "150", "80"],
    "conveyingbelt": ["mxgraph.pid2misc.conveyor", "150", "40"],
    "pressurefilter": ["mxgraph.pid.filters.press_filter", "91", "30"],
    "solidscentrifuge": [
        "mxgraph.pid.centrifuges.centrifuge_(solid_shell)",
        "100",
        "174",
    ],
    "reactor": ["mxgraph.pid.vessels.reactor", "160", "200"],
    "screwpress": ["mxgraph.pid.shaping_machines.extruder_(screw)", "100", "70"],
}

try:
    f = open("shapes.csv", "r")
    for line in f:
        line = line.split(",")
        if line[0] != "unit":
            shapes[line[0]] = [line[1], line[2], line[3]]
except:
    pass


def is_module_installed(module_name):
    try:
        importlib.import_module(module_name)
        return True
    except ImportError:
        return False


def get_shape(nodeID):
    shp = ["rectangle;rounded=1;strokeColor=#00f;fillColor=default", "100", "60"]
    for k in shapes.keys():
        if k.lower() in type(nodeID).__name__.lower():
            shp = shapes[k]
    return shp


def stream_width(stream, all_streams, measure):
    if measure == "mass":
        return (
            stream.get_total_flow("tonne/day")
            / max([s.get_total_flow("tonne/day") for s in all_streams])
            * 10
            + 5
        )
    elif measure == "carbon":
        return (
            stream.get_atomic_flow("C")
            / max([s.get_atomic_flow("C") for s in all_streams])
            * 10
            + 5
        )
    elif measure == "energy":
        return stream.H / max([s.H for s in all_streams]) * 10 + 5


def get_edges(system, measure):
    edges = []
    for s in system.streams:
        if measure == "mass":
            width = stream_width(s, system.streams, measure)
        elif measure == "carbon":
            width = stream_width(s, system.streams, measure)
        else:
            width = stream_width(s, system.streams, "mass")

        if s.source and s.sink:
            edges.append(
                {
                    "source": s.source.ID,
                    "target": s.sink.ID,
                    "width": width,
                    "label": s.ID,
                    "flow": "%.2f" % width,
                    "type": "edge",
                }
            )
        elif s.source and not s.sink:
            edges.append(
                {
                    "source": s.source.ID,
                    "target": None,
                    "width": width,
                    "label": s.ID,
                    "flow": "%.2f" % width,
                    "type": "edge",
                }
            )
        elif not s.source and s.sink:
            edges.append(
                {
                    "source": None,
                    "target": s.sink.ID,
                    "width": width,
                    "label": s.ID,
                    "flow": "%.2f" % width,
                    "type": "edge",
                }
            )
    return edges


def get_nodes(system):
    nodes = {}
    for u in system.units:
        nodes[u.ID] = {
            "unit": u,
            "label": u.ID,
            "name": u.__class__.__name__,
            "shape": get_shape(u),
        }
    return nodes


def ComputeHorizontalLayout(system, node, x, y, level):
    if node is None:
        return

    # Create a queue for BFS and add the root node along with its level (0)
    queue = []  # list of nodes and their x positions
    positions = {}  # list of nodes and their x and y positions
    feed_level = 0
    y = 1
    for node in system.feeds:
        queue.append([node, 0, y])

        # To store the nodes along with their calculated positions
        while len(queue) > 0:
            new_queue = queue
            queue = []

            for node, x, y in new_queue:
                # Store the node with its level
                positions[node] = (x, y)

                # Enqueue all children with their corresponding level
                if "sink" in dir(node) and node.sink and node.sink not in positions:
                    queue.append([node.sink, x + 1, y])
                    continue
                if "outs" in dir(node):
                    for child in node.outs:
                        if child and child.sink and child.sink not in positions:
                            queue.append([child.sink, x + 1, y])
                            y += 1
                            continue
                        if child and child not in positions:
                            queue.append([child, x + 1, y])
                            y += 1
    return positions


# shapes["furnace"] = ["mxgraph.pid.vessels.furnace", "80", "100"]
# draw_io2(sys, measure="mass", filename="flowsheet")


# %%
def find_paths(system, unit, path=[], start="", s=None):
    if unit:
        if unit in path:
            return path
        path = path + [unit]

        old_path = []
        for s in unit.outs:
            new_path = find_paths(system, s.sink, path, start, s)
            if len(new_path) > len(old_path):
                old_path = new_path
        path = old_path

        # else:
        #     s = unit.outs[0]
        #     if s and s.sink:
        #         return find_paths(system, s.sink, path, start)
        #     else:
        #         return find_paths(system, s.sink, path, start) + [s.ID]
    return path


def paths(system):
    paths = {}
    for s in system.feeds:
        path = []
        visited = []
        paths[s.ID] = find_paths(system, s.sink, [], s.ID)
    return paths


def longest_path(paths):
    longest_path = sorted(paths, key=lambda x: len(paths[x]), reverse=True)[0]
    return paths[longest_path]


# %%
def color_list(color):
    colors = [
        "white",
        "#fcaf17",  # Michael Scott's World's Best Boss mug yellow
        "#4877b9",  # Dunder Mifflin blue
        "#f26b6c",  # Pam's sweater pink
        "#6bd3c2",  # Jim's prank teal
        "#f4bb47",  # Dwight's mustard yellow
        "#7b8186",  # Office gray
        "#eb5e3e",  # Angela's cat poster orange
        "#b5a495",  # Stanley's desk brown
        "#3d854f",  # Kelly's green
        "#cc527a",  # Meredith's party pink
        "#4c4f53",  # Accounting gray
        "#8a6d3b",  # Creed's khaki
        "#6897bb",  # Andy's Cornell blue
        "#915e2b",  # Phyllis's dress brown
        "#c0c0c0",  # Conference room silver
        "#c27ba0",  # Erin's pink
    ]
    # wrap around
    if color >= len(colors):
        color = (color % len(colors)) - 1
    return colors[color]


# %%


def create_network(sys, graph, visited):
    for u in sys.units:
        if u not in visited:
            visited.append(u)
            subsys = u._system
            for s in sys.subsystems:
                for u1 in s.units:
                    if u1 == u:
                        subsys = s
            graph.add_node(u, layer=subsys.ID)
            for s in u.ins:
                if s.source == None:
                    graph.add_edge(s, u)
            for s in u.outs:
                if s.sink:
                    graph.add_edge(u, s.sink)
                    if s.sink._system:
                        create_network(s.sink._system, graph, visited)
                else:
                    graph.add_edge(u, s)
    return graph


# %%


#%%

#%%#%%
import sys 
sys.path.append("/Users/mark/Github/steamdrawio/src/steamdrawio/")


from ethanol import sys 
G, l = layout(sys)
#%%
draw(sys)

#%%
draw(sys, compounds=["Fiber", "Ethanol"], filename="test")
# %%
pos = {}
grid_x = 1
grid_y = 1
for (l, p) in zip(G.vs["label"], l.coords):
    pos[l] = [p[0] * grid_x, p[1] * grid_y]
# %%
pos
# %%
G
# %%
ig.plot(G)
# %%
path = sys.unit_path
groups = ["root"]
subsystems = sys.subsystems
for u in path:
    u.group = "root"
    for s in subsystems:
        if u in s.units:
            u.group = s.ID
            groups.append(s.ID)
groups = set(groups)
colors = dict([(g, color_list(i)) for i, g in enumerate(groups)])
groups
# %%
subsystems
# %%
sys.diagram('cluster', format="png")
# %%
for u in sys.units:
    print(u.ID, u.system.ID)
# %%
sys.subsystems[0].ID
# %%
