from graph import city


def accident(node1, node2):

    print("\n🚨 ACCIDENT REPORTED")
    print(f"📍 Location: {node1} → {node2}")
    print("🚧 Road status: BLOCKED")

    city.block_road(
        node1,
        node2
    )


def clear_accident(node1, node2):

    print("\n✅ ACCIDENT CLEARED")
    print(f"📍 Road: {node1} → {node2}")
    print("🛣️ Road status: OPEN")

    city.unblock_road(
        node1,
        node2
    )


def change_traffic(node1, node2, traffic):

    print("\n🚦 TRAFFIC UPDATE")
    print(f"📍 Road: {node1} → {node2}")
    print(f"Traffic multiplier: {traffic}")

    city.update_traffic(
        node1,
        node2,
        traffic
    )