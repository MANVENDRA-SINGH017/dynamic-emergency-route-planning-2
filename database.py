import mysql.connector


def get_connection():

    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="emergency_route_db"
    )

    return connection


# -----------------------------------------
# GET ALL ROADS
# -----------------------------------------

def get_roads():

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM roads
    """)

    roads = cursor.fetchall()

    cursor.close()
    connection.close()

    return roads


# -----------------------------------------
# RECORD INCIDENT
# -----------------------------------------

def save_incident(
    road_start,
    road_end,
    incident_type,
    description
):

    connection = get_connection()
    cursor = connection.cursor()

    query = """
        INSERT INTO incidents
        (road_start, road_end, incident_type, description)
        VALUES (%s, %s, %s, %s)
    """

    cursor.execute(
        query,
        (
            road_start,
            road_end,
            incident_type,
            description
        )
    )

    connection.commit()

    cursor.close()
    connection.close()


# -----------------------------------------
# SAVE ROUTE
# -----------------------------------------

def save_route(
    start,
    hospital,
    route,
    cost,
    reroutes
):

    connection = get_connection()
    cursor = connection.cursor()

    query = """
        INSERT INTO route_history
        (start_node, hospital_node, route, travel_cost, reroutes)
        VALUES (%s, %s, %s, %s, %s)
    """

    cursor.execute(
        query,
        (
            start,
            hospital,
            " -> ".join(route),
            cost,
            reroutes
        )
    )

    connection.commit()

    cursor.close()
    connection.close()

