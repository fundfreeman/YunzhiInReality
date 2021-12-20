import networkx as nx
from geopy.distance import geodesic
from typing import List, Union
from random import sample, choice

from networkx.algorithms.shortest_paths.generic import shortest_path
from networkx.classes.function import neighbors, path_weight
GEO_POINT = Union[float, float]

def T1Generate(graph : nx.Graph, points : List[GEO_POINT], min_distance : float, trigger_distance : float) -> List[GEO_POINT]:

    cycle = []
    
    for point in points:
        avail_node = list(filter((lambda n: geodesic(point, graph.nodes[n]['pos']).m <= trigger_distance), graph.nodes))
        if any(avail_node):
            cycle.append(choice(avail_node))

    
    pass_path = [cycle[0]]
    cycle_path = []
    distance = 0.0
    cycle_distance = 0.0
    last_point = cycle[0]
    
    for point in cycle[1:] + [cycle[0]]:
        path = shortest_path(graph, last_point, point, 'dis')
        cycle_path.extend(path[1:])
        cycle_distance += path_weight(graph, path, 'dis')
        last_point = point

    while distance < min_distance:
        pass_path += cycle_path
        distance += cycle_distance
    # while distance < min_distance:
    #     to = choice(neighbors(graph, pass_path[-1]))
    #     distance += graph[pass_path[-1]][to].dis
    #     pass_path.append(to)

    return [graph.nodes[i]['pos'] for i in pass_path]

def T2Generate(graph : nx.Graph, min_distance : float) -> List[GEO_POINT]:
    pass_path = [choice(graph)]
    distance = 0.0
    while distance < min_distance:
        to = choice(neighbors(graph, pass_path[-1]))
        distance += graph[pass_path[-1]][to].dis
        pass_path.append(to)

    return [graph.nodes[i]['pos'] for i in pass_path]

def T3Generate(graph : nx.Graph, points : List[GEO_POINT], point_num : int, min_distance : float, trigger_distance : float) -> List[GEO_POINT]:

    if len(points) < point_num:
        return None

    current_points = sample(points, point_num)
    return T1Generate(graph, current_points, min_distance, trigger_distance)
