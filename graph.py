
class CityGraph:

    def __init__(self):
        self.graph = {}
        self.coordinates = {}

    def add_node(self, node, x, y):
        self.graph[node] = []
        self.coordinates[node] = (x, y)

    def add_road(self, node1, node2, distance):
        road1 = {
            "node": node2,
            "distance": distance,
            "traffic": 1.0,
            "blocked": False
        }

        road2 = {
            "node": node1,
            "distance": distance,
            "traffic": 1.0,
            "blocked": False
        }

        self.graph[node1].append(road1)
        self.graph[node2].append(road2)

    def update_traffic(self, node1, node2, traffic):
        for road in self.graph[node1]:
            if road["node"] == node2:
                road["traffic"] = traffic

        for road in self.graph[node2]:
            if road["node"] == node1:
                road["traffic"] = traffic

    def block_road(self, node1, node2):
        for road in self.graph[node1]:
            if road["node"] == node2:
                road["blocked"] = True

        for road in self.graph[node2]:
            if road["node"] == node1:
                road["blocked"] = True

    def unblock_road(self, node1, node2):
        for road in self.graph[node1]:
            if road["node"] == node2:
                road["blocked"] = False

        for road in self.graph[node2]:
            if road["node"] == node1:
                road["blocked"] = False

    def reset_conditions(self):
        for node in self.graph:
            for road in self.graph[node]:
                road["traffic"] = 1.0
                road["blocked"] = False


city = CityGraph()

# City intersections: horizontal and vertical positions
city.add_node("A", 0, 2)
city.add_node("B", 2, 4)
city.add_node("C", 4, 4)
city.add_node("D", 6, 4)
city.add_node("E", 2, 2)
city.add_node("F", 4, 2)
city.add_node("G", 6, 2)
city.add_node("H", 8, 2)  # Hospital
city.add_node("I", 2, 0)
city.add_node("J", 4, 0)
city.add_node("K", 6, 0)
city.add_node("L", 8, 0)

# Main and alternative roads
city.add_road("A", "B", 4)
city.add_road("A", "E", 3)
city.add_road("B", "C", 3)
city.add_road("C", "D", 3)
city.add_road("E", "F", 2)
city.add_road("F", "G", 3)
city.add_road("G", "H", 3)
city.add_road("D", "H", 4)
city.add_road("E", "I", 3)
city.add_road("I", "J", 3)
city.add_road("J", "K", 3)
city.add_road("K", "L", 3)
city.add_road("L", "H", 4)
city.add_road("B", "E", 2)
city.add_road("C", "F", 2)
city.add_road("D", "G", 2)
city.add_road("F", "J", 2)