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


def get_shape(nodeID):
    shp = ["rectangle;rounded=1;strokeColor=#00f;fillColor=default", "100", "60"]
    for k in shapes.keys():
        if k.lower() in type(nodeID).__name__.lower():
            shp = shapes[k]
    return shp



def layout_system(
        sys
):
    G = ig.Graph(directed=True)
    vertices = {}
    i = 0
    for u in sys.units:
        vertices[u.ID] = i
        i += 1
    for s in sys.feeds:
        vertices[s.ID] = i
        i += 1
    for s in sys.products:
        vertices[s.ID] = i
        i += 1

    edges = []
    labels = []
    for u in sys.streams:
        if u.source and u.sink:
            edges.append((vertices[u.source.ID], vertices[u.sink.ID]))
            labels.append(u.ID)
        elif u.source and not u.sink:
            edges.append((vertices[u.source.ID], vertices[u.ID]))
            labels.append(u.ID)
        elif not u.source and u.sink:
            edges.append((vertices[u.ID], vertices[u.sink.ID]))
            labels.append(u.ID)
    G.add_vertices(len(vertices))
    G.add_edges(edges)

    G.vs["label"] = list(vertices.keys())
    
    G.es["label"] = labels

    l = G.layout("tree")
    l.rotate(270)
    l.mirror(1)
    return G, l

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


def generate_colors(groups):
    return dict([(g, color_list(i)) for i, g in enumerate(groups)])

def calculate_positions(G, layout, grid_x, grid_y):
    pos = {}
    for (l, p) in zip(G.vs["label"], layout.coords):
        pos[l] = [p[0] * grid_x, p[1] * grid_y]
    return pos

def create_root_element():
    root = ET.Element("mxGraphModel")
    root.set("dx", "846")
    root.set("dy", "900")
    root.set("grid", "1")
    root.set("gridSize", "10")
    root.set("guides", "1")
    root.set("tooltips", "1")
    root.set("connect", "1")
    root.set("arrows", "1")
    root.set("fold", "1")
    root.set("page", "1")
    root.set("pageScale", "1")
    root.set("pageWidth", "1150")
    root.set("pageHeight", "1150")
    root.set("math", "0")
    root.set("shadow", "0")
    root.append(ET.Comment("Created by the Sustainable Energy Systems Analysis Group"))
    return root

def write_xml_to_file(root, filename):
    tree = ET.ElementTree(root)
    if "png" in filename or "jpg" in filename:
        # [Code to handle image files]
        return filename
    else:
        with open(filename + ".drawio", "wb") as file:
            tree.write(file, encoding="utf-8", xml_declaration=True)
        return filename + ".drawio"

def place_units(parent, path, pos, colors):
    placed = []
    for u in path:
        if u.ID in placed:
            u.ID = u.ID+"x"
            print("Duplicate: " + u.ID)
        placed.append(u.ID)
        style = "shape=" + get_shape(u)[0] + ";" + f"fillColor={colors[u.system]};verticalLabelPosition=bottom;labelPosition=center;align=center;verticalAlign=top;"

        elem = ET.SubElement(parent, "mxCell")
        elem.set("id", u.ID)
        elem.set("value", u.ID)
        elem.set("style", style)
        elem.set("vertex", "1")
        elem.set("parent", "1")

        geometry = ET.SubElement(elem, "mxGeometry")
        geometry.set("x", str(pos[u.ID][0]))
        geometry.set("y", str(pos[u.ID][1]))
        geometry.set("width", get_shape(u)[1])
        geometry.set("height", get_shape(u)[2])
        geometry.set("relative", "0")
        geometry.set("as", "geometry")
    return parent

def connect_streams(parent, sys, pos):
    connected = []
    for s in sys.streams:
        if s.ID in connected:
            s.ID = s.ID+"x"
        connected.append(s.ID)
        elem = ET.SubElement(parent, "mxCell")
        elem.set("edge", "1")
        elem.set("parent", "1")
        elem.set(
            "style",
            "edgeStyle=elbowEdgeStyle;html=1;orthogonal=1;fontFamily=Helvetica;fontSize=18;align=center;",
        )

        geometry = ET.SubElement(elem, "mxGeometry")
        geometry.set("relative", "1")
        geometry.set("as", "geometry")
        if s.source and s.sink:
            elem.set("source", f"{s.source.ID}")
            elem.set("target", f"{s.sink.ID}")
            elem.set("value", f"{s.ID}")
            elem.set("id", f"s{s.ID}")

        elif s.source and s.sink==None:
            elem.set("id", f"o{s.ID}-{s.source.ID}")
            elem.set("source", f"{s.source.ID}")
            elem.set("target", f"o{s.ID}")
            # elem.set("value", f"{s.ID}")

            outNode = ET.SubElement(parent, "mxCell")
            outNode.set("id", f"o{s.ID}")
            outNode.set("value", f"{s.ID}")
            outNode.set(
                "style",
                "rounded=1;whiteSpace=wrap;html=1;fontFamily=Helvetica;fontSize=12;align=center;",
            )
            outNode.set("vertex", "1")
            outNode.set("parent", "1")

            geometry = ET.SubElement(outNode, "mxGeometry")
            geometry.set("x", str(pos[s.ID][0]))
            geometry.set("y", str(pos[s.ID][1]))
            geometry.set("width", str(100))
            geometry.set("height", str(60))
            geometry.set("as", "geometry")
        elif s.sink and s.source ==None:
            elem.set("id", f"i{s.ID}-{s.sink.ID}")
            elem.set("target", f"{s.sink.ID}")
            elem.set("source", f"i{s.ID}")
            inNode = ET.SubElement(parent, "mxCell")
            inNode.set("id", f"i{s.ID}")
            label = f"""{s.ID}"""
            inNode.set("value", label)
            # inNode.set("value", s.ID)
            inNode.set(
                "style",
                "rounded=1;whiteSpace=wrap;html=1;fontFamily=Helvetica;fontSize=18;align=center;",
            )
            inNode.set("vertex", "1")
            inNode.set("parent", "1")

            geometry = ET.SubElement(inNode, "mxGeometry")
            # geometry.set("x", str(0))
            # geometry.set("y", str(in_ys))
            geometry.set("x", str(pos[s.ID][0]))
            geometry.set("y", str(pos[s.ID][1]))
            geometry.set("width", str(100))
            geometry.set("height", str(60))
            geometry.set("as", "geometry")
    return parent

def add_stream_labels(parent, sys, compounds):
    for s in sys.streams:
        if s.source and s.sink:
            label = f"""{s.ID}\n"""
            if compounds is not None:
                for c in compounds:
                    if c in [c.ID for c in s.available_chemicals]:
                        label += f"""{c}: {s.imass[c]:.2f}\n"""
            elem = find_element(parent, f"{s.ID}")
            if elem is not None:
                elem.set("value", label)
    return parent

# Helper function to find an element
def find_element(parent, id):
    for elem in parent:
        if elem.get('id') == id:
            return elem
    return None

# Updated draw function
def draw(sys, filename="diagram", grid_x=300, grid_y=250, compounds=None):
    path = sys.unit_path
    groups = set(u.system for u in path)

    colors = generate_colors(groups)
    G, layout = layout_system(sys)
    pos = calculate_positions(G, layout, grid_x, grid_y)

    root = create_root_element()
    parent = ET.SubElement(root, "root")
    root_parent = ET.SubElement(parent, "mxCell")
    root_parent.set("id", "0")

    # Add default parent element
    default_parent = ET.SubElement(parent, "mxCell")
    default_parent.set("id", "1")
    default_parent.set("parent", "0")

    parent = place_units(parent, path, pos, colors)
    parent = connect_streams(parent, sys, pos)
    parent = add_stream_labels(parent, sys, compounds)

        # Write the XML tree to a file
    tree = ET.ElementTree(root)
    if "png" in filename or "jpg" in filename:
        ig.plot(G, target=filename)
        print(filename)
        return parent
    else:
        with open(filename + ".drawio", "wb") as file:
            tree.write(file, encoding="utf-8", xml_declaration=True)
        print(filename + ".drawio")
        return parent

#%%
# from ethanol import sys 
G, l = layout_system(sys)
#%%
ig.plot(G)
# %%
grid_x = 300
grid_y = 300
compounds = []
filename = "main"
path = sys.unit_path
groups = set(u.system for u in path)

colors = generate_colors(groups)
G, layout = layout_system(sys)
pos = calculate_positions(G, layout, grid_x, grid_y)

root = create_root_element()
parent = ET.SubElement(root, "root")
root_parent = ET.SubElement(parent, "mxCell")
root_parent.set("id", "0")

# Add default parent element
default_parent = ET.SubElement(parent, "mxCell")
default_parent.set("id", "1")
default_parent.set("parent", "0")

parent = place_units(parent, path, pos, colors)
parent = connect_streams(parent, sys, pos)
parent = add_stream_labels(parent, sys, compounds)

    # Write the XML tree to a file
tree = ET.ElementTree(root)
if "png" in filename or "jpg" in filename:
    ig.plot(G, target=filename)
    print(filename)
    # return parent
else:
    with open(filename + ".drawio", "wb") as file:
        tree.write(file, encoding="utf-8", xml_declaration=True)
    print(filename + ".drawio")
    # return parent
# %%
