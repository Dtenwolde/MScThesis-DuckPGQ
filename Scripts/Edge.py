class Edge:
    def __init__(self, source, destination, weight=1):
        self.source = source
        self.destination = destination
        self.weight = weight

    def __str__(self):
        return f"[{self.source}->{self.weight}{self.destination}]"

    __repr__ = __str__