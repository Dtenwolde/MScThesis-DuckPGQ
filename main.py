from Graph import Graph, BFS
from Node import Node
from random import randint

graph = Graph()

for i in range(6):
    graph.add_node(Node(i))

graph.nodes[0].add_edge(graph.nodes[0], graph.nodes[2], 1)
graph.nodes[2].add_edge(graph.nodes[2], graph.nodes[0], 1)
graph.nodes[0].add_edge(graph.nodes[0], graph.nodes[3], 1)
graph.nodes[3].add_edge(graph.nodes[3], graph.nodes[0], 1)
graph.nodes[1].add_edge(graph.nodes[1], graph.nodes[2], 1)
graph.nodes[2].add_edge(graph.nodes[2], graph.nodes[1], 1)
graph.nodes[1].add_edge(graph.nodes[1], graph.nodes[3], 10)
graph.nodes[3].add_edge(graph.nodes[3], graph.nodes[1], 1)
graph.nodes[2].add_edge(graph.nodes[2], graph.nodes[4], 1)
graph.nodes[4].add_edge(graph.nodes[4], graph.nodes[2], 1)
graph.nodes[3].add_edge(graph.nodes[3], graph.nodes[5], 2)
graph.nodes[5].add_edge(graph.nodes[5], graph.nodes[3], 1)


# graph.nodes[3].add_neighbour(graph.nodes[2])
# graph.nodes[2].add_neighbour(graph.nodes[4])
# graph.nodes[4].add_neighbour(graph.nodes[2])
# graph.nodes[3].add_neighbour(graph.nodes[5])
# graph.nodes[5].add_neighbour(graph.nodes[3])
# graph.nodes[4].add_neighbour(graph.nodes[6])
# graph.nodes[6].add_neighbour(graph.nodes[4])


# for i in range(10):
#     num_neighbours = randint(0,5)
#     for idx_neighbour in range(num_neighbours):
#         random_number = randint(0, 9)
#         while random_number == i:
#             random_number = randint(0,9)
#         graph.nodes[i].add_edge(graph.nodes[i], graph.nodes[random_number], 1)
#
# first_random = randint(0,9)
# second_random = randint(0,9)
# while first_random == second_random:
#     first_random = randint(0, 9)
#     second_random = randint(0, 9)
# graph.mf_bfs([BFS(first_random), BFS(second_random)], [first_random, second_random])
# graph.mf_bfs([BFS(1), BFS(2)], [1, 2])

graph.batched_bellman_ford([graph.nodes[0], graph.nodes[1]])