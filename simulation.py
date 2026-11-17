from graph import city
from astar import astar
from incident import accident, change_traffic
from database import save_route, save_incident


def simulate_ambulance(start, goal, scenario):

    current = start
    reroutes = 0
    total_cost = 0

    print("\n" + "=" * 55)
    print("        🚑 EMERGENCY ROUTE SIMULATION")
    print("=" * 55)

    print("\nEmergency Location:", start)
    print("Hospital:", goal)

    # -----------------------------------------
    # INITIAL ROUTE
    # -----------------------------------------

    path, cost = astar(
        city.graph,
        current,
        goal
    )

    if not path:
        print("\n❌ No route available.")
        return

    total_cost = cost

    print("\nInitial Route:")
    print(" → ".join(path))
    print("Initial Cost:", cost)

    i = 1

    while i < len(path):

        next_node = path[i]

        print(
            f"\n🚑 Ambulance travelling: "
            f"{current} → {next_node}"
        )

        # -----------------------------------------
        # ACCIDENT
        # -----------------------------------------

        if scenario == "accident" and reroutes == 0:

            print("\n⚠️ Accident detected ahead!")

            accident(current, next_node)

            # Save incident to MySQL
            save_incident(
                current,
                next_node,
                "ACCIDENT",
                "Road blocked because of an accident"
            )

            print("\n🔄 A* REPLANNING ROUTE...")

            new_path, new_cost = astar(
                city.graph,
                current,
                goal
            )

            if not new_path:

                print("❌ No alternative route available.")
                return

            reroutes += 1
            total_cost = new_cost

            print("\nNew Route:")
            print(" → ".join(new_path))

            print("New Cost:", new_cost)

            path = new_path

            i = 1

            continue

        # -----------------------------------------
        # TRAFFIC
        # -----------------------------------------

        if scenario == "traffic" and reroutes == 0:

            print("\n⚠️ Heavy traffic detected ahead!")

            change_traffic(
                current,
                next_node,
                4.0
            )

            # Save incident to MySQL
            save_incident(
                current,
                next_node,
                "TRAFFIC",
                "Traffic level increased"
            )

            print("\n🔄 A* REPLANNING ROUTE...")

            new_path, new_cost = astar(
                city.graph,
                current,
                goal
            )

            if not new_path:

                print("❌ No alternative route available.")
                return

            reroutes += 1
            total_cost = new_cost

            print("\nNew Route:")
            print(" → ".join(new_path))

            print("New Cost:", new_cost)

            path = new_path

            i = 1

            continue

        # -----------------------------------------
        # MOVE AMBULANCE
        # -----------------------------------------

        current = next_node
        i += 1

    # -----------------------------------------
    # ARRIVAL
    # -----------------------------------------

    print("\n" + "=" * 55)
    print("🏥 AMBULANCE ARRIVED")
    print("=" * 55)

    print("Final Location:", current)
    print("Total Reroutes:", reroutes)
    print("Final Travel Cost:", total_cost)

    # -----------------------------------------
    # SAVE ROUTE TO DATABASE
    # -----------------------------------------

    save_route(
        start,
        goal,
        path,
        total_cost,
        reroutes
    )

    print("\n💾 Route saved to MySQL.")


if __name__ == "__main__":

    simulate_ambulance(
        "A",
        "H",
        "accident"
    )

    # For traffic scenario:
    # simulate_ambulance("A", "H", "traffic")