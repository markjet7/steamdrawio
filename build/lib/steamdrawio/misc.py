def layout_nodes_old(system, path=None, row=1, column=1, node_positions=None):
    """Places the nodes in the longest path"""
    if path is None:
        path = compute_longest_path(system)
    if node_positions is None:
        node_positions = {}
    n = len(path)
    for i in range(n):
        if path[i].ID in node_positions.keys():
            pass
        else:
            if path[i].ID not in node_positions.keys():
                node_positions[path[i].ID] = (row+1, i+1)
            if "Stream" in str(type(path[i])):
                pass
            else:
                for j in range(0, len(path[i].outs)):
                    if path[i].outs[j].sink:
                        sub_lp = compute_longest_path_to_end(system, path[i].outs[j].ID)
                        if len(sub_lp) > 0:
                            nps = layout_nodes(system, sub_lp, row+1, j, node_positions)
                            [node_positions.update({k: v}) for k, v in nps.items()]
                        else:
                            node_positions[path[i].outs[j].sink.ID] = (row+1, j)
                    else:
                        node_positions[path[i].outs[j].ID] = (row+1, i+1)

    for f in system.feeds:
        row += 1
        column = 1
        if f.ID not in node_positions.keys():
            node_positions[f.ID] = (row, column)
            nps = layout_nodes(system, compute_longest_path_to_end(system, f.ID), row+1, 1, node_positions)
            for k, v in nps.items():
                if k not in node_positions.keys():
                    node_positions.update({k: v})
    return node_positions