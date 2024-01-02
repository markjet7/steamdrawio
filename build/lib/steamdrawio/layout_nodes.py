# The goal of this file/class is to create a horizontal flowchart
# it takes a list of nodes and a list of edges and creates a horizontal flowchart
# the nodes are placed based on the longest flow path 
# the edges are placed based on the nodes they connect to
# the nodes are placed in the middle of the longest flow path
# the edges are placed in the middle of the nodes they connect to

# To draw the flowchart, we first need to find the longest flow path
# The longest flow path is the path with the most nodes

# Then, we need to place the nodes in the middle of the longest flow path
# Branches from the longest flow path are placed in a lower row

# All rows then flow left to right

#%%
def find_path(system, u, v, recursion=0, recursion_limit=1000):
    """Finds the path between two units"""
    path = []
    if recursion > recursion_limit:
        print("Recursion limit reached")
        return []
    
    for e in system.streams:
        if e.source and e.source.ID == u:
            path.append(e.source.ID)
            if e.sink and e.sink.ID == v:
                path.append(e.sink.ID)
                return path
            elif e.ID == v:
                path.append(e.ID)
                return path
            else:
                if e.sink:
                    path += find_path(system, e.sink.ID, v, recursion=recursion+1)
                else:
                    return []
        elif e.ID == u:
            path.append(e.ID)
            if e.sink and e.sink.ID == v:
                path.append(e.sink.ID)
                return path
            elif e.ID == v:
                path.append(e.ID)
                return path
            else:
                if e.sink:
                    path += find_path(system, e.sink.ID, v, recursion=recursion+1)
                else:
                    return []
    if u in path and v in path:
        return path
    else:
        return []

# find_path(sys, "CornIn", "beer_column")
#%%
def path_length(system, u, v):
    """Computes the length of a path"""
    return len(find_path(system, u, v))

# path_length(sys, "grinding_mill", "beer_column")

#%%
def compute_longest_path(system):
    """Computes the longest path in a system"""
    ld = 0 # longest distance
    lp = [] # longest path

    for u in system.streams:
        for v in system.streams:
            if u != v:
                path = find_path(system, u.ID, v.ID)
                if len(path) > ld:
                    ld = len(path)
                    lp = path
    path = []
    for p in lp:
        if p in [s.ID for s in system.units]:
            path.append(system.flowsheet.unit[p])
        else:
            path.append(system.flowsheet.stream[p])
    return path

# compute_longest_path(sys)
#%%
def compute_longest_path_to_end(system, start):
    """Computes the longest path in a system"""
    ld = 0 # longest distance
    lp = [] # longest path

    for u in system.streams:
        path = find_path(system, start, u.ID)
        if len(path) > ld:
            ld = len(path)
            lp = path
    path = []
    for p in lp:
        if p in [s.ID for s in system.units]:
            path.append(system.flowsheet.unit[p])
        else:
            path.append(system.flowsheet.stream[p])
    return path

# compute_longest_path_to_end(sys, "CornIn")
# %%


def layout_nodes(system, path=None, x=1, y=1, node_positions=None, max_columns=4):
    """Places the nodes in the longest path, respecting a maximum column width."""
    if path is None:
        path = compute_longest_path(system)
    if node_positions is None:
        node_positions = {}
    
    for i in range(len(path)):
        if path[i].ID not in node_positions:
            # Update the row and column based on the current index and maximum columns
            # current_row = row + i // max_columns
            if x > max_columns:
                y += 1
                x = 1

            node_positions[path[i].ID] = (x, y)

            # Additional logic for 'Stream' and 'outs' remains unchanged
            if "Stream" not in str(type(path[i])): # if not a stream
                for j in range(len(path[i].outs)): # for each out
                    if path[i].outs[j].sink: # if the out has a sink (i.e. not a feed)
                        sub_lp = compute_longest_path_to_end(system, path[i].outs[j].ID) # compute the longest path to the end
                        if sub_lp:
                            if x < max_columns:
                                x += 1
                            else:
                                y = max([v[1] for v in node_positions.values()]) + 1
                                x = 1
                            nps = layout_nodes(system, sub_lp, x, y, node_positions, max_columns)
                            node_positions.update(nps)
                        else:
                            node_positions[path[i].outs[j].sink.ID] = (x + 1, y+j)
                    else:
                        node_positions[path[i].outs[j].ID] = (max_columns+1, y)
        x += 1
    
    return node_positions


layout_nodes(sys)
drawDecember(sys, "mass", "testing", 300, 300)

#%%
def layout_feeds(system, node_positions):
    """Places the feeds within 2 rows of the sink"""

    adjusted = []
    for f in system.feeds:
        positions = [[0, -2], [0, 2], [1, -2], [1, 2], [2, -2], [2, 2]]
        sink = f.sink
        sink_position = node_positions[sink.ID]
        p =0
        for i in sink.ins:
            if i.source == None and i.ID not in adjusted:
                node_positions[i.ID] = (sink_position[0]+positions[p][0], sink_position[1]+positions[p][1])
                adjusted.append(i.ID)
                p += 1
                print(i.ID, node_positions[i.ID], sink_position)
    return node_positions

def layout(system):
    """Places the nodes in the longest path"""
    node_positions = layout_nodes(system, max_columns=5)
    node_positions = layout_feeds(system, node_positions)
    return node_positions

# %%
"dryer" in list(l.keys())
# %%
