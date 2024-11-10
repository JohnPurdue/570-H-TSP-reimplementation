def cluster_node(node):
    x, y = node['coord']
    
    if x <= 1/3:
        if y <= 1/3:
            cluster = 1
        elif y <= 2/3:
            cluster = 2
        else:
            cluster = 3
    elif x <= 2/3:
        if y <= 1/3:
            cluster = 4
        elif y <= 2/3:
            cluster= 5
        else:
            cluster = 6
    else:
        if y <= 1/3:
            cluster = 7
        elif y <= 2/3:
            cluster = 8
        else:
            cluster = 9
    return cluster


def center_relative_coord(node):
    x, y = node['coord']
    return (x - 0.5, y - 0.5)


def cluster_relative_coord(node):
    x, y = node['coord']
    cluster_centers = {
        1: (1/6, 1/6),
        2: (1/6, 1/2),
        3: (1/6, 5/6),
        4: (1/2, 1/6),
        5: (1/2, 1/2),
        6: (1/2, 5/6),
        7: (5/6, 1/6),
        8: (5/6, 1/2),
        9: (5/6, 5/6)
    }
    cluster_center = cluster_centers[node['cluster']]
    return (x - cluster_center[0], y - cluster_center[1])


def augment_data(graph):
    
    for node in graph.nodes:
        graph.nodes[node]['number'] = node
        graph.nodes[node]['cluster'] = cluster_node(graph.nodes[node])
        graph.nodes[node]['center_relative_coord'] = center_relative_coord(graph.nodes[node])
        graph.nodes[node]['cluster_relative_coord'] = cluster_relative_coord(graph.nodes[node])
        graph.nodes[node]['prev_coord'] = (0.0, 0.0)
        graph.nodes[node]['next_coord'] = (0.0, 0.0)
        graph.nodes[node]['visited'] = False
        # print(graph.nodes[node])
    return graph
