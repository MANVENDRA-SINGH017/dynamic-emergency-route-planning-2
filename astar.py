from graph import city
import math
import heapq


def heuristic(node, goal):

    x1, y1 = city.coordinates[node]
    x2, y2 = city.coordinates[goal]

    straight_distance = math.sqrt(
        (x2 - x1) ** 2 +
        (y2 - y1) ** 2
    )

    # Find the minimum distance-to-cost ratio
    min_ratio = float("inf")

    for roads in city.graph.values():

        for road in roads:

            ratio = road["distance"] / max(
                road["distance"],
                0.0001
            )

            min_ratio = min(
                min_ratio,
                ratio
            )

    return straight_distance * min_ratio


def astar(graph, start, goal):

    priority_queue = []

    heapq.heappush(
        priority_queue,
        (0, 0, start, [start])
    )

    visited = set()

    while priority_queue:

        f_cost, current_cost, current, path = heapq.heappop(
            priority_queue
        )

        if current == goal:
            return path, current_cost

        if current in visited:
            continue

        visited.add(current)

        for road in graph[current]:

            neighbor = road["node"]
            distance = road["distance"]
            traffic = road["traffic"]
            blocked = road["blocked"]

            # Ignore blocked roads
            if blocked:
                continue

            # Calculate travel cost
            road_cost = distance * traffic

            new_cost = current_cost + road_cost

            h_cost = heuristic(neighbor, goal)

            total_cost = new_cost + h_cost

            new_path = path + [neighbor]

            if neighbor not in visited:

                heapq.heappush(
                    priority_queue,
                    (
                        total_cost,
                        new_cost,
                        neighbor,
                        new_path
                    )
                )

    return None, float("inf")