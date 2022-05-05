from Edge import Edge


class Node:
    def __init__(self, id):
        self.id = id
        self.edges = []

    def add_edge(self, source, destination, weight):
        self.edges.append(Edge(source, destination, weight))

    def __str__(self):
        return f"({self.id}), {[edge.destination.id for edge in self.edges]})"

    __repr__ = __str__
