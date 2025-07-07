# ToDo: Change to https://n2g.readthedocs.io/en/latest/diagram_plugins/DrawIo%20Module.html

# %%
import pprint
import xml.etree.ElementTree as ET
import random
import importlib


import igraph as ig

import plotly.graph_objects as go
import matplotlib.pyplot as plt

# from layout_nodes import *

# %%

shapes = {
    "unit": ["process", "140", "100"],
    "boiler": ["mxgraph.pid.vessels.furnace", "160", "200"],
    "mixer": ["mxgraph.pid.mixers.in-line_static_mixer", "70", "70"],
    "isentropiccompressor": ["mxgraph.pid.engines.turbine;flipH=1,", "70", "100"],
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
    "drumdryer": ["mxgraph.pid.driers.rotary_drum_drier,_tumbling_drier", "85", "120"],
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
    for (i, u) in enumerate(sys.units + sys.feeds + sys.products):
        # check if the first letter is a number
        if u.ID == "":
            u.ID = "u" + str(i)
        if u.ID[0].isdigit():
            u.ID = "u" + u.ID
        if u.ID in vertices.keys():
            u.ID = u.ID+"2"
        vertices[u.ID] = i

    edges = []
    labels = []
    def get_vertices(id):
        if id in vertices.keys():
            return vertices[id]
        else:
            vertices[id] = len(vertices)
            return vertices[id]
    for u in sys.streams:
        if u.source and u.sink:
            edges.append((get_vertices(u.source.ID), get_vertices(u.sink.ID)))
            labels.append(u.ID)
        elif u.source and not u.sink:
            edges.append((get_vertices(u.source.ID), get_vertices(u.ID)))
            labels.append(u.ID)
        elif not u.source and u.sink:
            edges.append((get_vertices(u.ID), get_vertices(u.sink.ID)))
            labels.append(u.ID)
    G.add_vertices(len(vertices))
    G.add_edges(edges)

    G.vs["label"] = list(vertices.keys())
    
    G.es["label"] = labels

    l = G.layout("tree")
    l.rotate(270)
    l.mirror(1)
    l.scale([2, 1])
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
    root.set("dx", "500")
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
            # u.ID = u.ID+"_"
            continue
        placed.append(u.ID)
        style = "shape=" + get_shape(u)[0] + ";" + f"fillColor={colors[u.system]};verticalLabelPosition=bottom;labelPosition=center;align=center;verticalAlign=top;fontSize=20;"

        elem = ET.SubElement(parent, "mxCell")
        elem.set("id", u.ID)
        elem.set("value", u.ID.replace("_", " "))
        elem.set("style", style)
        elem.set("vertex", "1")
        elem.set("parent", "1")

        geometry = ET.SubElement(elem, "mxGeometry")
        geometry.set("x", str(pos[u.ID][0]))
        geometry.set("y", str(pos[u.ID][1] + float(get_shape(u)[2])/2))
        geometry.set("width", get_shape(u)[1])
        geometry.set("height", get_shape(u)[2])
        geometry.set("relative", "0")
        geometry.set("as", "geometry")
    return parent

def connect_streams(parent, sys, pos):
    connected = []
    for s in sys.streams:
        if s.ID in connected:
            # s.ID = s.ID+"_"
            continue
        connected.append(s.ID)
        elem = ET.SubElement(parent, "mxCell")
        elem.set("edge", "1")
        elem.set("parent", "1")
        elem.set(
            "style",
            f"edgeStyle=elbowEdgeStyle;html=1;orthogonal=1;fontFamily=Helvetica;fontSize=20;align=center;strokeWidth=6;",
        )
        elem.set(
            "connectable",
            "0",
        )

        geometry = ET.SubElement(elem, "mxGeometry")
        geometry.set("relative", "1")
        geometry.set("as", "geometry")
        if s.source and s.sink:
            elem.set("id", f"{s.ID}")
            elem.set("source", f"{s.source.ID}")
            elem.set("target", f"{s.sink.ID}")
            elem.set("value", f"{s.ID.replace('_', ' ')}")

        elif s.source and s.sink==None:
            elem.set("id", f"o{s.ID}")
            elem.set("source", f"{s.source.ID}")
            elem.set("target", f"o{s.ID}l")
            # elem.set("value", f"{s.ID}")

            outNode = ET.SubElement(parent, "mxCell")
            outNode.set("id", f"o{s.ID}l")
            outNode.set("value", f"{s.ID.replace('_', ' ')}")
            outNode.set(
                "style",
                "rounded=1;whiteSpace=wrap;html=1;fontFamily=Helvetica;fontSize=42;align=center;",
            )
            outNode.set("vertex", "1")
            outNode.set("parent", "1")

            geometry = ET.SubElement(outNode, "mxGeometry")
            geometry.set("x", str(pos[s.ID][0]))
            geometry.set("y", str(pos[s.ID][1]-25))
            geometry.set("width", str(400))
            geometry.set("height", str(100))
            geometry.set("as", "geometry")
        elif s.sink and s.source ==None:
            elem.set("id", f"i{s.ID}")
            elem.set("target", f"{s.sink.ID}")
            elem.set("source", f"i{s.ID}l")
            inNode = ET.SubElement(parent, "mxCell")
            inNode.set("id", f"i{s.ID}l")
            label = f"""{s.ID.replace('_', ' ')}"""
            inNode.set("value", label)
            # inNode.set("value", s.ID)
            inNode.set(
                "style",
                "rounded=1;whiteSpace=wrap;html=1;fontFamily=Helvetica;fontSize=42;align=center;",
            )
            inNode.set("vertex", "1")
            inNode.set("parent", "1")

            geometry = ET.SubElement(inNode, "mxGeometry")
            # geometry.set("x", str(0))
            # geometry.set("y", str(in_ys))
            geometry.set("x", str(pos[s.ID][0]))
            geometry.set("y", str(pos[s.ID][1]))
            geometry.set("width", str(400))
            geometry.set("height", str(100))
            geometry.set("as", "geometry")
    return parent

def move_outlets_to_right(parent, sys):
    max_x = 0
    for s in sys.streams:
        if s.source and s.sink==None:
            elem = find_element(parent, f"o{s.ID}l")
            if elem is not None:
                # print(dir(elem))
                max_x = max(max_x, float(elem.find("mxGeometry").get("x")))

    for s in sys.streams:
        if s.source and s.sink==None:
            elem = find_element(parent, f"o{s.ID}l")
            if elem is not None:
                elem.find("mxGeometry").set("x", str(max_x+400))
    return parent

def spread_inlets(parent, sys, pos):
    # find units with multiple inlets
    # spread the inlets from top (entryY= 0.99) to bottom (entryY=0.01) based on the source of the inlet
    print("Spreading inlets")
    def sourceID(x):
        if x.source:
            return x.source.ID
        else:
            return x.ID

    for s in sys.units:
        inlets = [i for i in s.ins if i]
        if len(inlets) > 1:

            inlets.sort(key=lambda x: pos[sourceID(x)][1])
            for i, inlet in enumerate(inlets):
                elem = find_element(parent, f"i{inlet.ID}")
                if elem is not None:
                    elem.set("style", elem.get("style") + f"entryY={i*1/(len(inlets)+1)+0.05};entryX=0;entryDx=0;entryDy=0;entryPerimeter=0;")
    return parent

# def add_stream_labels(parent, sys, compounds):
#     for s in sys.streams:
#         if s.source and s.sink:
#             label = f"""{s.ID.replace('_', ' ')}"""
#             if compounds is not None:
#                 for c in compounds:
#                     if c in [c.ID for c in s.available_chemicals]:
#                         label += f"""{c}: {s.imass[c]:.2f}\n"""
#             elem = find_element(parent, f"{s.ID}")
#             if elem is not None:
#                 elem.set("value", label)
#     return parent

# def add_unit_labels(parent, sys):
#     for u in sys.units:
#         elem = find_element(parent, f"{u.ID}")
#         if elem is not None:
#             elem.set("value", u.ID)
#     return parent

def add_stream_labels(parent, sys, label_function):
    for s in sys.streams:
        try:
            label = label_function(s)
            elem = find_element(parent, f"{s.ID}")
            if elem is not None:
                elem.set("value", label)
        except Exception as e:
            print(f"Error in adding custom label to stream {s.ID}: {e}")
            pass
    return parent

def add_unit_labels(parent, sys, label_function):
    for u in sys.units:
        try:
            label = label_function(u)
            elem = find_element(parent, f"{u.ID}")
            if elem is not None:
                elem.set("value", label)
        except Exception as e:
            print(f"Error in adding custom label to unit {u.ID}: {e}")
            print("Elem: ", elem)
            print("Label_fn: ", label_function)
            pass
    return parent

# Helper function to find an element
def find_element(parent, id):
    for elem in parent:
        if elem.get('id') == id:
            return elem
        if elem.get('id') == f"o{id}" or elem.get('id') == f"i{id}":
            return elem
    return None

def draw(sys, filename="diagram", grid_x=300, grid_y=250, compounds=None, label_fn=None, label_units_fn=None, backend="drawio"):
    if backend.lower() == "drawio":
        drawIO(sys, filename, grid_x, grid_y, compounds, label_fn, label_units_fn)
    elif backend.lower() == "plotly":
        drawPlotly(sys, filename, grid_x, grid_y, compounds, label_fn, label_units_fn)
    elif backend.lower() == "matplotlib":
        drawMatplotlib(sys, filename, grid_x, grid_y, compounds, label_fn, label_units_fn)
    elif backend.lower() == "pillow":
        drawPillow(sys, filename, grid_x, grid_y, compounds, label_fn, label_units_fn)

# Updated draw function
def drawIO(sys, filename="diagram", grid_x=300, grid_y=250, compounds=None, label_fn=None, label_units_fn=None):

    from IPython.display import display

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
    parent = move_outlets_to_right(parent, sys)
    parent = spread_inlets(parent, sys, pos)
    if label_fn is not None:
        parent = add_stream_labels(parent, sys, label_fn)
    if label_units_fn is not None:
        parent = add_unit_labels(parent, sys, label_units_fn)
    


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

        xml = ET.tostring(root, encoding="unicode")
        display({"application/x-drawio": xml}, raw=True)
        
        return parent
# draw(system, backend="drawio", grid_x=100, grid_y=100)
#%%
def drawPlotly(sys, filename="diagram", grid_x=300, grid_y=250, compounds=None, label_fn=None, label_units_fn=None):
    path = sys.unit_path
    groups = set(u.system for u in path)

    colors = generate_colors(groups)
    G, layout = layout_system(sys)
    pos = calculate_positions(G, layout, grid_x, grid_y)

    print(pos)

    fig = go.Figure()

    for u in path:
        fig.add_shape(
            type="rect",
            x0=pos[u.ID][0],
            y0=pos[u.ID][1],
            x1=pos[u.ID][0] +  len(u.ID)*180,
            y1=pos[u.ID][1] + grid_y/2,
            line=dict(color="black", width=2),
            label={"texttemplate": u.ID},
        )

    for s in sys.streams:
        if s.source and s.sink:
            fig.add_trace(
                go.Scatter(
                    x=[pos[s.source.ID][0]+50, pos[s.sink.ID][0]-50],
                    y=[pos[s.source.ID][1]+50, pos[s.sink.ID][1]+50],
                    mode="lines",
                    line=dict(color="black", width=2),
                    showlegend=False,
                )
            )
        elif s.source and not s.sink:
            fig.add_shape(
                type="rect",
                x0=pos[s.ID][0],
                y0=pos[s.ID][1],
                x1=pos[s.ID][0] + len(s.ID)*180,
                y1=pos[s.ID][1] + grid_y/2,
                line=dict(color="black", width=2),
                fillcolor="white",
                label={"texttemplate": s.ID},
            )
            fig.add_trace(
                go.Scatter(
                    x=[pos[s.source.ID][0], pos[s.ID][0]],
                    y=[pos[s.source.ID][1]+50, pos[s.ID][1]+50],
                    mode="lines",
                    line=dict(color="black", width=2),
                    showlegend=False,
                )
            )
        elif not s.source and s.sink:
            fig.add_shape(
                type="rect",
                x0=pos[s.ID][0],
                y0=pos[s.ID][1],
                x1=pos[s.ID][0] + len(s.ID)*grid_x/7,
                y1=pos[s.ID][1] + grid_y/2,
                line=dict(color="black", width=2),
                fillcolor="white",
                label={"texttemplate": s.ID},
            )
            fig.add_trace(
                go.Scatter(
                    x=[pos[s.ID][0] + len(s.ID)*180, pos[s.sink.ID][0]],
                    y=[pos[s.ID][1]+50, pos[s.sink.ID][1]+50],
                    mode="lines",
                    line=dict(color="black", width=2),
                    showlegend=False,
                )
            )

    fig.update_layout(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        autosize=True,
        showlegend=False,
        font=dict(size=12),
    )
    fig.write_html(filename + ".html")
    print(filename + ".html")
    fig.show()
    return fig

def drawPillow(sys, filename="diagram", grid_x=300, grid_y=250, compounds=None, label_fn=None, label_units_fn=None):
    path = sys.unit_path
    groups = set(u.system for u in path)

    colors = generate_colors(groups)
    G, layout = layout_system(sys)
    pos = calculate_positions(G, layout, grid_x, grid_y)
    print(pos)

    from PIL import Image, ImageDraw, ImageFont
    from IPython.display import display

    img = Image.new("RGB", (int(max([x[0] for x in pos.values()])*1.2), int(max([x[1] for x in pos.values()])*1.2)), color = (255, 255, 255))
    d = ImageDraw.Draw(img)
    fnt = ImageFont.load_default()
    for u in path:
        d.rectangle(
            [pos[u.ID][0], pos[u.ID][1], pos[u.ID][0] +  len(u.ID)*6, pos[u.ID][1] + 30],
            outline="black",
            fill=(255, 255, 255),
        )
        d.text((pos[u.ID][0], pos[u.ID][1]+7), u.ID, font=fnt, fill=(0, 0, 0))

    for s in sys.streams:
        if s.source and s.sink:
            d.line(
                [pos[s.source.ID][0]+len(s.source.ID)*6, pos[s.source.ID][1]+15, pos[s.sink.ID][0], pos[s.sink.ID][1]+15],
                fill="black",
                width=2,
            )
        elif s.source and not s.sink:
            d.rectangle(
                [pos[s.source.ID][0], pos[s.source.ID][1]+15, pos[s.source.ID][0]+len(s.source.ID)*6, pos[s.source.ID][1] + 15],
                outline="black",
                fill=(255, 255, 255),
            )
            d.text((pos[s.ID][0], pos[s.ID][1]), s.ID, font=fnt, fill=(0, 0, 0))
            d.line(
                [pos[s.source.ID][0]+len(s.source.ID)*6, pos[s.source.ID][1]+15, pos[s.ID][0], pos[s.ID][1]],
                fill="black",
                width=2,
            )
        elif not s.source and s.sink:
            d.rectangle(
                [pos[s.ID][0], pos[s.ID][1], pos[s.ID][0] + len(s.ID)*6, pos[s.ID][1] + 30],
                outline="black",
                fill=(255, 255, 255),
            )
            d.text((pos[s.ID][0], pos[s.ID][1]), s.ID, font=fnt, fill=(0, 0, 0))
            d.line(
                [pos[s.ID][0] + len(s.ID)*6, pos[s.ID][1]+15, pos[s.sink.ID][0], pos[s.sink.ID][1]+15],
                fill="black",
                width=2,
            )

    img.save(filename + ".png")
    print(filename + ".png")
    display(img)
    return img

#%% Testing

import sys 
sys.path.append("./src/steamdrawio/")


from ethanol import system

# %%

draw(system, backend="drawio", grid_x=100, grid_y=100)

#%%