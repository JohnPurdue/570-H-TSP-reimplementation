def solveSubproblem(graph, nodes, start_node, end_node):
    
    # print('subsolving:', nodes)
    ordered_nodes = [start_node]
    nodes.remove(start_node)
    nodes.remove(end_node)
    
    while len(nodes) > 0:
        ordered_nodes.append(nodes.pop())
    ordered_nodes.append(end_node)
    return ordered_nodes
