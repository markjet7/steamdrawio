# %%
import xml.etree.ElementTree as ET
import random 
import networkx as nx
# %%

shapes = {'unit': ['process', '140', '100'],
 'mixer': ['mxgraph.pid.mixers.in-line_static_mixer', '70', '20'],
 'pump': ['mxgraph.pid.pumps.centrifugal_pump_1', '70', '70'],
 'steammixer': ['mxgraph.pid.piping.in-line_mixer', '100', '100'],
 'mockmixer': ['mxgraph.pid.piping.in-line_mixer', '60', '20'],
 'splitter': ['mxgraph.pid.filters.filter', '30', '30'],
 'phasesplitter': ['mxgraph.pid.separators.separator_(cyclone)2',
  '100',
  '100'],
 'mocksplitter': ['mxgraph.pid.filters.filter', '80', '120'],
 'reversedsplitter': ['mxgraph.pid.filters.filter', '30', '30'],
 'molecularsieve': ['mxgraph.pid.misc.screening_device,_sieve,_strainer',
  '100',
  '50'],
 'hx': ['mxgraph.pid.heat_exchangers.fixed_straight_tubes_heat_exchanger',
  '50',
  '10'],
 'hxutility': ['mxgraph.pid.heat_exchangers.heater', '100', '60'],
 'hxprocess': ['mxgraph.pid.heat_exchangers.condenser', '100', '60'],
 'tank': ['mxgraph.pid.vessels.tank_(dished_roof)', '200', '120'],
 'mixtank': ['mxgraph.pid.vessels.jacketed_mixing_vessel', '200', '240'],
 'storagetank': ['mxgraph.pid.vessels.tank_(floating_roof)', '160', '240'],
 'distillation': ['mxgraph.pid.vessels.tower_with_packing', '160', '240'],
 'binarydistillation': ['mxgraph.pid.vessels.tower_with_packing',
  '200',
  '220'],
 'shortcutcolumn': ['mxgraph.pid.vessels.tower_with_packing', '200', '220'],
 'duplicator': ['process', '100', '100'],
 'junction': ['process', '100', '140'],
 'massbalance': ['process', '100', '140'],
 'diagramonlyunit': ['process', '80', '80'],
 'diagramonlysystemunit': ['process', '80', '80'],
 'diagramonlystreamunit': ['process', '100', '40'],
 'flash': ['mxgraph.pid.separators.spray_scrubber', '100', '100'],
 'splitflash': ['mxgraph.pid.separators.spray_scrubber', '70', '67'],
 'ratioflash': ['mxgraph.pid.separators.spray_scrubber', '110', '60'],
 'multieffectevaporator': ['mxgraph.pid.heat_exchangers.condenser',
  '100',
  '95'],
 'solidsseparator': ['mxgraph.pid.separators.separator_(electromagnetic)',
  '14',
  '97'],
 'rotaryvacuumfilter': ['mxgraph.pid.filters.press_filter', '52', '95'],
 'crushingmill': ['mxgraph.pid.crushers_grinding.crusher_(hammer)',
  '80',
  '99'], 
  'hammermill': ['mxgraph.pid.crushers_grinding.crusher_(hammer)',
  '80',
  '99'],
  'conveyingbelt':['mxgraph.pid2misc.conveyor', '150', '40'],
 'pressurefilter': ['mxgraph.pid.filters.press_filter', '91', '30'],
 'solidscentrifuge': ['mxgraph.pid.centrifuges.centrifuge_(solid_shell)',
  '100',
  '174'],
  'reactor': ['mxgraph.pid.vessels.reactor', '160', '240'],
 'screwpress': ['mxgraph.pid.shaping_machines.extruder_(screw)', '100', '70']}

def get_shape(nodeID):
    shp = ["rectangle;rounded=1;strokeColor=#00f;fillColor=default", "100", "60"]
    for k in shapes.keys():
        if k.lower() in type(nodeID).__name__.lower():
            shp = shapes[k]
    return shp 

def stream_width(stream, all_streams, measure):
    if measure == "mass":
        return stream.get_total_flow('tonne/day') / max([s.get_total_flow('tonne/day') for s in all_streams]) * 10 + 5
    elif measure == "carbon":
        return stream.get_atomic_flow('C') / max([s.get_atomic_flow('C') for s in all_streams]) * 10 + 5
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
            edges.append({"source":s.source.ID, "target":s.sink.ID, "width":width, "label":s.ID, "flow":"%.2f" % width, "type": "edge"})
        elif s.source and not s.sink:
            edges.append({"source":s.source.ID, "target":None, "width":width, "label":s.ID, "flow":"%.2f" % width, "type": "edge"})
        elif not s.source and s.sink:
            edges.append({"source":None, "target":s.sink.ID, "width":width, "label":s.ID, "flow":"%.2f" % width, "type": "edge"})
    return edges

def get_nodes(system):
    nodes = {}
    for u in system.units:
        nodes[u.ID] = ({"unit": u, "label": u.ID, "name":u.__class__.__name__, "shape":get_shape(u)})
    return nodes

def ComputeHorizontalLayout(system, node, x, y, level):
    if node is None:
        return
    
    # Create a queue for BFS and add the root node along with its level (0)
    queue = []
    queue.append([node, 0])

    # To store the nodes along with their calculated positions
    positions = {
        node: (0, 0)
    } 
    while len(queue) > 0:
        node, level = queue.pop() 

 
        # If this level hasn't been visited before, its order (x position) will be 0
        levels = [level for node, (level, order) in positions.items()]
        if level not in levels:
            positions[node] = (level, 1)
        else:
            lastOrder = max([order for node, (level, order) in positions.items() if level == level])
          
            positions[node] = (level, lastOrder + 1)

        # Enqueue all children with their corresponding level
        for child in node.outs:
            if child and child.sink and child.sink not in positions:
                queue.append([child.sink, level + 1])

    return positions

def draw_io_old(system, measure="mass", filename="flowsheet"):
    edges = get_edges(system, measure)
    nodes = get_nodes(system)
    

    # Create the root element
    root = ET.Element('mxGraphModel')
    root.set('dx', '846')
    root.set('dy', '680')
    root.set('grid', '1')
    root.set('gridSize', '10')
    root.set('guides', '1')
    root.set('tooltips', '1')
    root.set('connect', '1')
    root.set('arrows', '1')
    root.set('fold', '1')
    root.set('page', '1')
    root.set('pageScale', '1')
    root.set('pageWidth', '827')
    root.set('pageHeight', '1169')
    root.set('math', '0')
    root.set('shadow', '0')

    root.append(ET.Comment('Created with Python'))

    parent = ET.SubElement(root, 'root')
    root_parent = ET.SubElement(parent, 'mxCell')
    root_parent.set('id', '0')

    # Add default parent element
    default_parent = ET.SubElement(parent, 'mxCell')
    default_parent.set('id', '1')
    default_parent.set('parent', '0')
    # default_parent.set('style', 'swimlane;html=1;startSize=20;horizontal=0;childLayout=flowLayout;flowOrientation=west;resizable=1;interRankCellSpacing=50;containerType=tree;fontSize=12;verticalAlign=center;labelPosition=center;verticalLabelPosition=bottom;align=center;swimlaneFillColor=#FFCE9F;strokeColor=none;fillColor=none;rounded=1;shadow=1;')

    parents = set(["container_" + n["unit"]._system.ID if n["unit"]._system.ID else "root" for n in nodes.values()])
    parent_ys = 0
    for p in parents:
        elem = ET.SubElement(parent, 'mxCell')
        elem.set('id', p)
        elem.set('value', p)
        elem.set('style', 'swimlane;html=1;startSize=20;horizontal=0;childLayout=flowLayout;flowOrientation=west;resizable=1;interRankCellSpacing=50;containerType=tree;fontSize=12;verticalAlign=middle;labelPosition=center;verticalLabelPosition=middle;align=center;swimlaneFillColor=none;strokeColor=default;fillColor=none;rounded=1;shadow=1;labelBorderColor=none;')
        elem.set('vertex', '1')
        elem.set('parent', '1')

        geometry = ET.SubElement(elem, 'mxGeometry')
        geometry.set('x', str(0))
        geometry.set('y', str(parent_ys))
        geometry.set('width', str(1000))
        geometry.set('height', str(200))
        geometry.set('as', 'geometry')

        parent_ys += 300
    
    # Add nodes to XML tree
    posx = 0
    posy = 0
    for node in nodes.values():
        elem = ET.SubElement(parent, 'mxCell')
        elem.set('id', str(node['label']))
        elem.set('value', node['label'])
        elem.set('style', "shape=" + node['shape'][0]+";")
        elem.set('vertex', '1')
        if node['unit']._system.ID:
            elem.set('parent', "container_" + node['unit']._system.ID)
        else:
            elem.set('parent', '1')


        geometry = ET.SubElement(elem, 'mxGeometry')
        geometry.set('x', str(posx))
        geometry.set('y', str(posy))
        geometry.set('width', node['shape'][1])
        geometry.set('height', node['shape'][2])
        geometry.set('as', 'geometry')

        posx = posx + 100
        node['x'] = posx 
        node['y'] = posy
        if posx > 800:
            posx = 0
            posy = posy + 100

    # Add edges to XML tree
    ins = 0
    outs = 0
    for edge in edges:
        elem = ET.SubElement(parent, 'mxCell')
        if edge['source'] == None:
            elem.set('id', f'i{ins}')
            ins += 1
        elif edge['target'] == None:
            elem.set('id', f'o{outs}')
            outs += 1
        else:
            elem.set('id', f'e{edge["source"]}-{edge["target"]}')
            if nodes[edge['source']]["unit"]._system.ID:
                elem.set('parent', "container_" + nodes[edge['source']]["unit"]._system.ID)

        strokeWidth = float(edge['flow'])/max([float(e['flow']) for e in edges]) * 3 + 2
        elem.set('style', 'edgeStyle=orthogonalEdgeStyle;strokeWidth=' + str(strokeWidth))
        elem.set('edge', '1')

        if (edge['source'] == None):
            inNode = ET.SubElement(parent, 'mxCell')
            inNode.set('id', f'in{ins}')
            inNode.set('value', edge['label'])
            inNode.set('style', 'rounded=1;whiteSpace=wrap;html=1;fontFamily=Helvetica;fontSize=12;align=center;')
            inNode.set('vertex', '1')
            inNode.set('parent', '1')

            geometry = ET.SubElement(inNode, 'mxGeometry')
            geometry.set('x', str(0))
            geometry.set('y', str(ins*20))
            geometry.set('width', str(100))
            geometry.set('height', str(60))
            geometry.set('as', 'geometry')

            elem.set('source', f'in{ins}')
        else:
            elem.set('source', str(edge['source']))

        if (edge['target'] == None):
            outNode = ET.SubElement(parent, 'mxCell')
            outNode.set('id', f'out{outs}')
            outNode.set('value', edge['label'])
            outNode.set('style', 'rounded=1;whiteSpace=wrap;html=1;fontFamily=Helvetica;fontSize=12;align=center;')
            outNode.set('vertex', '1')
            outNode.set('parent', '1')

            geometry = ET.SubElement(outNode, 'mxGeometry')
            geometry.set('x', str(800))
            geometry.set('y', str(outs*20))
            geometry.set('width', str(100))
            geometry.set('height', str(60))
            geometry.set('as', 'geometry')

            elem.set('target', f'out{outs}')
        else:
            elem.set('target', str(edge['target']))

        geometry = ET.SubElement(elem, 'mxGeometry')
        geometry.set('relative', '1')
        geometry.set('as', 'geometry')

        elem.set('parent', '1')

        # geometry = ET.SubElement(elem, 'mxGeometry')
        # geometry.set('relative', '1')
        # geometry.set('as', 'geometry')


    # Write the XML tree to a file
    tree = ET.ElementTree(root)
    with open(filename+'.drawio', 'wb') as file:
        tree.write(file, encoding='utf-8', xml_declaration=True)

# %%
def draw_io2(system, measure="mass", filename="diagram"):

    # Create the root element
    root = ET.Element('mxGraphModel')
    root.set('dx', '846')
    root.set('dy', '680')
    root.set('grid', '1')
    root.set('gridSize', '10')
    root.set('guides', '1')
    root.set('tooltips', '1')
    root.set('connect', '1')
    root.set('arrows', '1')
    root.set('fold', '1')
    root.set('page', '1')
    root.set('pageScale', '1')
    root.set('pageWidth', '827')
    root.set('pageHeight', '1169')
    root.set('math', '0')
    root.set('shadow', '0')

    root.append(ET.Comment('Created with Python'))

    parent = ET.SubElement(root, 'root')
    root_parent = ET.SubElement(parent, 'mxCell')
    root_parent.set('id', '0')

    # Add default parent element
    default_parent = ET.SubElement(parent, 'mxCell')
    default_parent.set('id', '1')
    default_parent.set('parent', '0')

    # Find out how many shapes are in each group
    group_shapes = {}
    for u in system.units:
        if u._system.ID:
            if u._system.ID in group_shapes.keys():
                group_shapes[u._system.ID] += 1
            else:
                group_shapes[u._system.ID] = 1
    
    group_x = 0
    group_regions = {}
    for p in group_shapes.keys():
        group_regions[p] = [group_x, 0]
        elem = ET.SubElement(parent, 'mxCell')
        elem.set('id', "group_" + p)
        elem.set('value', p)
        elem.set('style', "group")
        elem.set('vertex', '1')
        elem.set('connectable', '0')
        elem.set('parent', '1')

        geometry = ET.SubElement(elem, 'mxGeometry')
        geometry.set('x', str(group_x))
        geometry.set('y', str(0))
        geometry.set('width', str(200*group_shapes[p]))
        geometry.set('height', '300')
        geometry.set('as', 'geometry')
        group_x += 50 + 200*group_shapes[p]

    x = 0
    y = 0
    path = system._unit_path
    group_xs = {}
    for u in path:
        elem = ET.SubElement(parent, 'mxCell')
        elem.set('id', u.ID)
        elem.set('value', u.ID)
        elem.set('style', "shape=" + get_shape(u)[0]+";")
        elem.set('vertex', '1')
        elem.set('parent', '1')
        if u._system.ID:
            elem.set('parent', "group_" + u._system.ID)
        else:
            u._system.ID = "root"

        if u._system.ID not in group_xs.keys():
            group_xs[u._system.ID] = 0

        
        print(u.ID, u._system.ID, group_regions.get(u._system.ID, [0, 0])[0]+x, group_regions.get(u._system.ID, [0, 0])[1]+y)

        geometry = ET.SubElement(elem, 'mxGeometry')
        geometry.set('x', str(group_xs[u._system.ID]))
        geometry.set('y', '150')
        geometry.set('width', get_shape(u)[1])
        geometry.set('height', get_shape(u)[2])
        geometry.set('as', 'geometry')
        
        group_xs[u._system.ID] += float(get_shape(u)[1])+50
        
        for s in u.outs:
            elem = ET.SubElement(parent, 'mxCell')
            elem.set('edge', '1')
            geometry = ET.SubElement(elem, 'mxGeometry')
            geometry.set('relative', '1')
            geometry.set('as', 'geometry')
            elem.set('parent', '1')
            if s.source and s.sink:
                elem.set('id', f'e{s.source.ID}-{s.sink.ID}')
                elem.set('style', 'edgeStyle=elbowEdgeStyle;html=1;orthogonal=1;elbow=vertical;fontFamily=Helvetica;fontSize=12;align=center;')
                elem.set('source', f'{s.source.ID}')
                elem.set('target', f'{s.sink.ID}')
            else:
                elem.set('source', f'{u.ID}')
                elem.set('target', f'o{s.ID}')
                outNode = ET.SubElement(parent, 'mxCell')
                outNode.set('id', f'o{s.ID}')
                outNode.set('value', s.ID)
                outNode.set('style', 'rounded=1;whiteSpace=wrap;html=1;fontFamily=Helvetica;fontSize=12;align=center;')
                outNode.set('vertex', '1')
                outNode.set('parent', '1')

                geometry = ET.SubElement(outNode, 'mxGeometry')
                geometry.set('x', str(group_regions[u._system.ID][0] + group_xs[u._system.ID]))
                geometry.set('y', str(y))
                geometry.set('width', str(100))
                geometry.set('height', str(60))
                geometry.set('as', 'geometry')
            y += 200
        
        for s in u.ins:
            u_y = y
            elem = ET.SubElement(parent, 'mxCell')
            elem.set('edge', '1')
            elem.set('parent', '1')
            elem.set('id', f'i{s.ID}-{u.ID}')
            geometry = ET.SubElement(elem, 'mxGeometry')
            geometry.set('relative', '1')
            geometry.set('as', 'geometry')
            if s.source == None:
                elem.set('target', f'{u.ID}')
                elem.set('source', f'i{s.ID}')
                inNode = ET.SubElement(parent, 'mxCell')
                inNode.set('id', f'i{s.ID}')
                inNode.set('value', s.ID)
                inNode.set('style', 'rounded=1;whiteSpace=wrap;html=1;fontFamily=Helvetica;fontSize=12;align=center;')
                inNode.set('vertex', '1')
                inNode.set('parent', '1')

                geometry = ET.SubElement(inNode, 'mxGeometry')
                geometry.set('x', str(group_regions.get(u._system.ID, [0, 0])[0]+x-200))
                geometry.set('y', str(u_y))
                geometry.set('width', str(100))
                geometry.set('height', str(60))
                geometry.set('as', 'geometry')
                u_y += 200
        y = 0
        x += float(get_shape(u)[1])+50

    # Write the XML tree to a file
    tree = ET.ElementTree(root)
    with open(filename+'.drawio', 'wb') as file:
        tree.write(file, encoding='utf-8', xml_declaration=True)


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
        "#c27ba0"   # Erin's pink
    ]
    # wrap around
    if color >= len(colors):
        color = (color % len(colors)) -1
    return colors[color]


# %%
def draw_io3(sys, measure="mass", filename="diagram"):
    path = sys._unit_path

    orders_and_levels = ComputeHorizontalLayout(sys, sys.units[0], 0, 0, 0)
    max_order = max(orders_and_levels.values())[0]
    groups = ["root"]
    subsystems = sys.subsystems
    for u in path:
        for s in subsystems:
            if u in s.units:
                u.group = s.ID
                groups.append(s.ID)
    groups = set(groups)
    # Create the root element
    root = ET.Element('mxGraphModel')
    root.set('dx', '846')
    root.set('dy', '680')
    root.set('grid', '1')
    root.set('gridSize', '10')
    root.set('guides', '1')
    root.set('tooltips', '1')
    root.set('connect', '1')
    root.set('arrows', '1')
    root.set('fold', '1')
    root.set('page', '1')
    root.set('pageScale', '1')
    root.set('pageWidth', '827')
    root.set('pageHeight', '1169')
    root.set('math', '0')
    root.set('shadow', '0')

    root.append(ET.Comment('Created with Python'))

    parent = ET.SubElement(root, 'root')
    root_parent = ET.SubElement(parent, 'mxCell')
    root_parent.set('id', '0')

    # Add default parent element
    default_parent = ET.SubElement(parent, 'mxCell')
    default_parent.set('id', '1')
    default_parent.set('parent', '0')

    margin = 50
    padding = 10
    layout = {}
    unit_width = 210
    unit_height = 200


    color = 0
    for g in groups:
        # collect all the group units
        group_units = [u for u in path if u.group == g]
        group_orders = {}
        for u in group_units:
            if u in orders_and_levels.keys():
                group_orders[u] = orders_and_levels[u][0]
            else:
                group_orders[u] = random.randint(1,10) + 1
                orders_and_levels[u] = [group_orders[u], 1]
            # dict([(u,orders_and_levels[u][0]) for u in group_units])

        # identify the bounds of the group
        if len(group_units) > 0:
            min_order = min(group_orders.values())
            for unit in group_units:
                layout[unit] = [(group_orders[unit]-min_order)*unit_width, orders_and_levels[unit][1]]

            # add group element
            elem = ET.SubElement(parent, 'mxCell')
            elem.set('id', "group_" + g)
            elem.set('value', g)
            elem.set('style', f"group;strokeColor=default;rounded=1;glass=0;shadow=0;fillColor={color_list(color)};")
            color += 1
            elem.set('vertex', '1')
            elem.set('connectable', '0')
            elem.set('parent', '1')

            geometry = ET.SubElement(elem, 'mxGeometry')
            geometry.set('x', str(min_order*unit_width*1.1 + 2*margin))
            geometry.set('y', str(min([orders_and_levels[u][1] for u in group_units])*unit_height+2*margin))
            geometry.set('width', str(len(group_units)*unit_width))
            geometry.set('height', str(len(set([orders_and_levels[u][1] for u in group_units]))*unit_height*0.8))
            geometry.set('as', 'geometry')
            geometry.set('recursiveResize', '0')
    
    in_ys = 0
    out_ys = 0
    for u in path:
        elem = ET.SubElement(parent, 'mxCell')
        elem.set('id', u.ID)
        elem.set('value', u.ID)
        elem.set('style', "shape=" + get_shape(u)[0]+";")
        elem.set('vertex', '1')
        elem.set('parent', '1')
        if u.group:
            elem.set('parent', "group_" + u.group)
        else:
            u.group = "root"

        geometry = ET.SubElement(elem, 'mxGeometry')
        geometry.set('x', str(layout[u][0]+padding))
        geometry.set('y', str(layout[u][1]+2*padding))
        geometry.set('width', get_shape(u)[1])
        geometry.set('height', get_shape(u)[2])
        geometry.set('relative', '0')
        geometry.set('as', 'geometry')

        
        for s in u.outs:
            elem = ET.SubElement(parent, 'mxCell')
            elem.set('edge', '1')
            geometry = ET.SubElement(elem, 'mxGeometry')
            geometry.set('relative', '1')
            geometry.set('as', 'geometry')
            elem.set('parent', '1')
            if s.source and s.sink:
                elem.set('id', f'e{s.source.ID}-{s.sink.ID}')
                elem.set('style', 'edgeStyle=elbowEdgeStyle;html=1;orthogonal=1;elbow=vertical;fontFamily=Helvetica;fontSize=12;align=center;')
                elem.set('source', f'{s.source.ID}')
                elem.set('target', f'{s.sink.ID}')
                elem.set('value', s.ID)
            else:
                elem.set('source', f'{u.ID}')
                elem.set('target', f'o{s.ID}')
                elem.set('style', 'edgeStyle=elbowEdgeStyle;html=1;orthogonal=1;elbow=vertical;fontFamily=Helvetica;fontSize=12;align=center;')
                outNode = ET.SubElement(parent, 'mxCell')
                outNode.set('id', f'o{s.ID}')
                outNode.set('value', s.ID)
                outNode.set('style', 'rounded=1;whiteSpace=wrap;html=1;fontFamily=Helvetica;fontSize=12;align=center;')
                outNode.set('vertex', '1')
                outNode.set('parent', '1')

                geometry = ET.SubElement(outNode, 'mxGeometry')
                geometry.set('x', str(max_order*unit_width*1.1 + 2*margin))
                geometry.set('y', str(out_ys))
                geometry.set('width', str(100))
                geometry.set('height', str(60))
                geometry.set('as', 'geometry')
                out_ys += 150
        
        for s in u.ins:
            elem = ET.SubElement(parent, 'mxCell')
            elem.set('edge', '1')
            elem.set('parent', '1')
            elem.set('id', f'i{s.ID}-{u.ID}')
            elem.set('style', 'edgeStyle=elbowEdgeStyle;html=1;orthogonal=1;elbow=vertical;fontFamily=Helvetica;fontSize=12;align=center;')
            geometry = ET.SubElement(elem, 'mxGeometry')
            geometry.set('relative', '1')
            geometry.set('as', 'geometry')
            if s.source == None:
                elem.set('target', f'{u.ID}')
                elem.set('source', f'i{s.ID}')
                inNode = ET.SubElement(parent, 'mxCell')
                inNode.set('id', f'i{s.ID}')
                inNode.set('value', s.ID)
                inNode.set('style', 'rounded=1;whiteSpace=wrap;html=1;fontFamily=Helvetica;fontSize=12;align=center;')
                inNode.set('vertex', '1')
                inNode.set('parent', '1')

                geometry = ET.SubElement(inNode, 'mxGeometry')
                geometry.set('x', str(0))
                geometry.set('y', str(in_ys))
                geometry.set('width', str(100))
                geometry.set('height', str(60))
                geometry.set('as', 'geometry')
                in_ys += 150

    # Write the XML tree to a file
    filename = "diagram"
    tree = ET.ElementTree(root)
    with open(filename+'.drawio', 'wb') as file:
        tree.write(file, encoding='utf-8', xml_declaration=True)

# draw_io(sys, measure="mass", filename="flowsheet")
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
                    create_network(s.sink._system, graph, visited)
                else:
                    graph.add_edge(u, s)
    return graph

# %%
def draw_io(sys, measure="mass", filename="diagram"):
    G = nx.DiGraph()
    visited = []
    G = create_network(sys, G, visited)
    pos = nx.nx_agraph.graphviz_layout(G, prog='dot', args='-Grankdir=LR -Gminlen=2 -Gnodesep=2.5 -Granksep=1.2')
    path = sys._unit_path

    groups = ["root"]
    subsystems = sys.subsystems
    for u in path:
        for s in subsystems:
            if u in s.units:
                u.group = s.ID
                groups.append(s.ID)
    groups = set(groups)
    colors = dict([(g, color_list(i)) for i, g in enumerate(groups)])
    # Create the root element
    root = ET.Element('mxGraphModel')
    root.set('dx', '846')
    root.set('dy', '900')
    root.set('grid', '1')
    root.set('gridSize', '10')
    root.set('guides', '1')
    root.set('tooltips', '1')
    root.set('connect', '1')
    root.set('arrows', '1')
    root.set('fold', '1')
    root.set('page', '1')
    root.set('pageScale', '1')
    root.set('pageWidth', '1200')
    root.set('pageHeight', '1200')
    root.set('math', '0')
    root.set('shadow', '0')

    root.append(ET.Comment('Created by the Sustainable Energy Systems Analysis Group'))

    parent = ET.SubElement(root, 'root')
    root_parent = ET.SubElement(parent, 'mxCell')
    root_parent.set('id', '0')

    # Add default parent element
    default_parent = ET.SubElement(parent, 'mxCell')
    default_parent.set('id', '1')
    default_parent.set('parent', '0')

    margin = 50
    padding = 10
    layout = {}
    unit_width = 210
    unit_height = 200


    in_ys = 0
    out_ys = 0
    for u in path:
        style = "shape=" + get_shape(u)[0]+";"+f"fillColor={colors[u.group]};"

        elem = ET.SubElement(parent, 'mxCell')
        elem.set('id', u.ID)
        elem.set('value', u.ID)
        elem.set('style', style)
        elem.set('vertex', '1')
        elem.set('parent', '1')
        # if u.group:
        #     elem.set('parent', "group_" + u.group)
        # else:
        #     u.group = "root"

        geometry = ET.SubElement(elem, 'mxGeometry')
        geometry.set('x', str(pos[u][0]))
        geometry.set('y', str(pos[u][1]))
        geometry.set('width', get_shape(u)[1])
        geometry.set('height', get_shape(u)[2])
        geometry.set('relative', '0')
        geometry.set('as', 'geometry')
        
        for s in u.outs:
            elem = ET.SubElement(parent, 'mxCell')
            elem.set('edge', '1')
            geometry = ET.SubElement(elem, 'mxGeometry')
            geometry.set('relative', '1')
            geometry.set('as', 'geometry')
            elem.set('parent', '1')
            if s.source and s.sink:
                elem.set('id', f'e{s.source.ID}-{s.sink.ID}')
                elem.set('style', 'edgeStyle=elbowEdgeStyle;html=1;orthogonal=1;elbow=vertical;fontFamily=Helvetica;fontSize=18;align=center;')
                elem.set('source', f'{s.source.ID}')
                elem.set('target', f'{s.sink.ID}')
                elem.set('value', s.ID)
            else:
                elem.set('source', f'{u.ID}')
                elem.set('target', f'o{s.ID}')
                elem.set('style', 'edgeStyle=elbowEdgeStyle;html=1;orthogonal=1;elbow=vertical;fontFamily=Helvetica;fontSize=18;align=center;')
                outNode = ET.SubElement(parent, 'mxCell')
                outNode.set('id', f'o{s.ID}')
                outNode.set('value', s.ID)
                outNode.set('style', 'rounded=1;whiteSpace=wrap;html=1;fontFamily=Helvetica;fontSize=12;align=center;')
                outNode.set('vertex', '1')
                outNode.set('parent', '1')

                geometry = ET.SubElement(outNode, 'mxGeometry')
                geometry.set('x', str(pos[s][0]))
                geometry.set('y', str(pos[s][1]))
                geometry.set('width', str(100))
                geometry.set('height', str(60))
                geometry.set('as', 'geometry')
                out_ys += 150
        
        for s in u.ins:
            elem = ET.SubElement(parent, 'mxCell')
            elem.set('edge', '1')
            elem.set('parent', '1')
            elem.set('id', f'i{s.ID}-{u.ID}')
            elem.set('style', 'edgeStyle=elbowEdgeStyle;html=1;orthogonal=1;elbow=vertical;fontFamily=Helvetica;fontSize=12;align=center;')
            geometry = ET.SubElement(elem, 'mxGeometry')
            geometry.set('relative', '1')
            geometry.set('as', 'geometry')
            if s.source == None:
                elem.set('target', f'{u.ID}')
                elem.set('source', f'i{s.ID}')
                inNode = ET.SubElement(parent, 'mxCell')
                inNode.set('id', f'i{s.ID}')
                inNode.set('value', s.ID)
                inNode.set('style', 'rounded=1;whiteSpace=wrap;html=1;fontFamily=Helvetica;fontSize=18;align=center;')
                inNode.set('vertex', '1')
                inNode.set('parent', '1')

                geometry = ET.SubElement(inNode, 'mxGeometry')
                geometry.set('x', str(0))
                geometry.set('y', str(in_ys))
                geometry.set('width', str(100))
                geometry.set('height', str(60))
                geometry.set('as', 'geometry')
                in_ys += 150

    # Write the XML tree to a file
    tree = ET.ElementTree(root)
    with open(filename+'.drawio', 'wb') as file:
        tree.write(file, encoding='utf-8', xml_declaration=True)

# draw_io(sys, measure="mass", filename="networkx_graph")
# %%
