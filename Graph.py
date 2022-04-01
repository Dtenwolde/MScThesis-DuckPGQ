from Edge import Edge
from Node import Node

class BFS:
    def __init__(self, source_id):
        self.source_id = source_id

    def __str__(self):
        return f"bfs{self.source_id}"

    __repr__ = __str__


class Graph:
    def __init__(self):
        self.nodes = []

    def add_node(self, node: Node):
        self.nodes.append(node)

    # def bfs(self, source_id = -1):
    #     seen = {self.nodes[source_id]}
    #     visit = {self.nodes[source_id]}
    #     visit_next = set()
    #     reachable = [source_id]
    #
    #     while visit:
    #         for node in list(visit):
    #             for neighbour in node.neighbours:
    #                 if neighbour not in seen:
    #                     seen.add(neighbour)
    #                     visit_next.add(neighbour)
    #                     print(f"Seen {neighbour.id}")
    #                     reachable.append(neighbour.id)
    #         visit = visit_next
    #         visit_next = set()
    #     print("Finished BFS")
    #     print(f"Reachable nodes: {reachable}")
    #
    # def mf_bfs(self, B, S):
    #     seen = {}
    #     path_length = {}
    #     for idx, b in enumerate(B):
    #         seen[self.nodes[S[idx]]] = [b]
    #         path_length[b.source_id] = {(b.source_id, 0)}
    #
    #     visit = set()
    #     for idx, b in enumerate(B):
    #         visit.add((self.nodes[S[idx]], tuple([b])))
    #     visit_next = set()
    #
    #     hop_counter = 1
    #     while visit:
    #         for node in visit:
    #             B_v_prime = []
    #             for bfs_set in visit:
    #                 if node == bfs_set:
    #                     B_v_prime.append(bfs_set[1][0])
    #             for neighbour in node[0].neighbours:
    #                 try:
    #                     seen_neighbourid = seen[neighbour]
    #                 except KeyError:
    #                     seen_neighbourid = []
    #                 D = list(set(B_v_prime) - set(seen_neighbourid))
    #                 if D:
    #                     visit_next.add((neighbour, tuple(D)))
    #                     if neighbour not in seen:
    #                         seen[neighbour] = D
    #                     else:
    #                         for bfs in D:
    #                             seen[neighbour].append(bfs)
    #
    #                     # if neighbour.id not in path_length:
    #                     for bfs in D:
    #                         try:
    #                             for t in path_length[neighbour.id]:
    #                                 if t[0] == bfs.source_id:
    #                                     continue
    #                                 path_length[neighbour.id].add((bfs.source_id, hop_counter))
    #                                 break
    #                         except KeyError:
    #                             path_length[neighbour.id] = {(bfs.source_id, hop_counter)}
    #         hop_counter += 1
    #         visit = visit_next
    #         visit_next = set()
    #
    #     for k, v in self.nodes.items():
    #         print(k, v.neighbours)
    #
    #     print(path_length)
    #     print(seen)

    def batched_bellman_ford(self, sources):
        dists = [[float('inf') for _ in sources] for _ in self.nodes]
        modified = [[False for _ in sources] for _ in self.nodes]

        for i in range(len(sources)):
            v = sources[i]
            dists[v.id][i] = 0
            modified[v.id][i] = True
        print(dists)
        print(modified)

        changed = True
        while changed:
            changed = False
            for v in self.nodes:
                if any(modified[v.id]):
                    for n in v.edges:
                        weight = n.weight
                        for i in range(len(modified[v.id])):
                            if modified[v.id][i]:
                                new_dist = min(dists[n.destination.id][i], dists[v.id][i] + weight)
                                if new_dist != dists[n.destination.id][i]:
                                    dists[n.destination.id][i] = new_dist
                                    modified[n.destination.id][i] = True
                                    changed = True
        print(dists)
        print(self.nodes)