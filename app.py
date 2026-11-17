
import random
import tkinter as tk
from tkinter import ttk, messagebox

from graph import city
from astar import astar
from incident import accident, change_traffic
from database import save_route, save_incident


# ===================== THEME =====================

BG = "#101820"
PANEL = "#18232F"
PANEL_LIGHT = "#202F3D"
ROAD = "#43515F"
ROAD_EDGE = "#657483"
BLUE = "#3694FF"
RED = "#FF555D"
ORANGE = "#FFA940"
GREEN = "#37D996"
WHITE = "#F1F5F9"
MUTED = "#9AA9B8"


class EmergencyRouteApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Emergency Route Planner")
        self.root.geometry("1350x800")
        self.root.minsize(1100, 700)
        self.root.configure(bg=BG)

        self.current_route = []
        self.traffic_road = None
        self.start_node = "A"
        self.goal_node = "H"
        self.current_status = "NORMAL"

        self.setup_styles()
        self.create_interface()
        self.draw_map()

    # ===================== STYLES =====================

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Dark.TCombobox",
            fieldbackground=PANEL_LIGHT,
            background=PANEL_LIGHT,
            foreground=WHITE,
            arrowcolor=WHITE,
            bordercolor=PANEL_LIGHT,
            padding=7
        )

    def make_label(
        self, parent, text, size=10,
        color=WHITE, bold=False
    ):
        return tk.Label(
            parent,
            text=text,
            font=(
                "Segoe UI",
                size,
                "bold" if bold else "normal"
            ),
            bg=parent.cget("bg"),
            fg=color
        )

    def make_button(
        self, parent, text, command,
        color=BLUE
    ):
        return tk.Button(
            parent,
            text=text,
            command=command,
            font=("Segoe UI", 10, "bold"),
            bg=color,
            fg="white",
            activebackground=color,
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=10
        )

    # ===================== INTERFACE =====================

    def create_interface(self):

        # Top navigation bar
        header = tk.Frame(self.root, bg=PANEL, height=75)
        header.pack(fill="x")
        header.pack_propagate(False)

        brand = tk.Frame(header, bg=PANEL)
        brand.pack(side="left", padx=24, pady=12)

        tk.Label(
            brand,
            text="🚑",
            font=("Segoe UI Emoji", 25),
            bg=PANEL,
            fg=WHITE
        ).pack(side="left", padx=(0, 12))

        title_box = tk.Frame(brand, bg=PANEL)
        title_box.pack(side="left")

        self.make_label(
            title_box,
            "EMERGENCY ROUTE PLANNER",
            15, WHITE, True
        ).pack(anchor="w")

        self.make_label(
            title_box,
            "INTELLIGENT NAVIGATION SYSTEM  /  A* SEARCH",
            8, MUTED
        ).pack(anchor="w", pady=(3, 0))

        self.status_badge = tk.Label(
            header,
            text="● SYSTEM READY",
            font=("Segoe UI", 10, "bold"),
            bg=PANEL,
            fg=GREEN
        )
        self.status_badge.pack(side="right", padx=25)

        # Main layout
        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True, padx=16, pady=14)

        # Left: map
        map_section = tk.Frame(body, bg=BG)
        map_section.pack(
            side="left", fill="both", expand=True
        )

        map_heading = tk.Frame(map_section, bg=BG)
        map_heading.pack(fill="x", pady=(0, 10))

        self.make_label(
            map_heading,
            "CITY ROAD NETWORK",
            12, WHITE, True
        ).pack(side="left")

        self.make_label(
            map_heading,
            "SIMULATED ENVIRONMENT",
            9, MUTED
        ).pack(side="right")

        self.map_canvas = tk.Canvas(
            map_section,
            bg="#202B35",
            highlightthickness=1,
            highlightbackground="#344454"
        )
        self.map_canvas.pack(fill="both", expand=True)

        # Right: controls and route details
        sidebar = tk.Frame(
            body,
            bg=PANEL,
            width=315
        )
        sidebar.pack(
            side="right", fill="y", padx=(14, 0)
        )
        sidebar.pack_propagate(False)

        self.make_label(
            sidebar, "ROUTE CONFIGURATION",
            12, WHITE, True
        ).pack(anchor="w", padx=18, pady=(20, 14))

        self.make_label(
            sidebar, "Emergency location", 9, MUTED
        ).pack(anchor="w", padx=18)

        self.start_box = ttk.Combobox(
            sidebar,
            values=list(city.graph.keys()),
            state="readonly",
            style="Dark.TCombobox"
        )
        self.start_box.set("A")
        self.start_box.pack(
            fill="x", padx=18, pady=(5, 12)
        )

        self.make_label(
            sidebar, "Destination / Hospital",
            9, MUTED
        ).pack(anchor="w", padx=18)

        self.goal_box = ttk.Combobox(
            sidebar,
            values=list(city.graph.keys()),
            state="readonly",
            style="Dark.TCombobox"
        )
        self.goal_box.set("H")
        self.goal_box.pack(
            fill="x", padx=18, pady=(5, 12)
        )

        self.make_label(
            sidebar, "Traffic / incident simulation",
            9, MUTED
        ).pack(anchor="w", padx=18)

        self.scenario_box = ttk.Combobox(
            sidebar,
            values=[
                "Normal",
                "Accident",
                "Heavy Traffic",
                "Random Obstacles"
            ],
            state="readonly",
            style="Dark.TCombobox"
        )
        self.scenario_box.set("Normal")
        self.scenario_box.pack(
            fill="x", padx=18, pady=(5, 14)
        )

        self.make_button(
            sidebar,
            "▶  FIND OPTIMAL ROUTE",
            self.find_route
        ).pack(fill="x", padx=18, pady=(0, 20))

        self.make_label(
            sidebar, "LIVE ROUTE STATUS",
            10, MUTED, True
        ).pack(anchor="w", padx=18)

        self.status_text = tk.Label(
            sidebar,
            text="● NORMAL CONDITIONS",
            bg=PANEL_LIGHT,
            fg=GREEN,
            font=("Segoe UI", 10, "bold"),
            padx=10,
            pady=12,
            anchor="w"
        )
        self.status_text.pack(
            fill="x", padx=18, pady=(7, 16)
        )

        # Route summary cards
        metrics = tk.Frame(sidebar, bg=PANEL)
        metrics.pack(fill="x", padx=18)

        self.cost_value = self.metric(
            metrics, "TRAVEL COST", "—"
        )
        self.reroute_value = self.metric(
            metrics, "REROUTES", "0"
        )

        self.make_label(
            sidebar, "CALCULATED ROUTE",
            10, MUTED, True
        ).pack(anchor="w", padx=18, pady=(18, 8))

        self.route_text = tk.Label(
            sidebar,
            text="Choose locations and find a route.",
            bg=PANEL_LIGHT,
            fg=WHITE,
            font=("Segoe UI", 11, "bold"),
            wraplength=265,
            justify="left",
            padx=12,
            pady=14,
            anchor="w"
        )
        self.route_text.pack(
            fill="x", padx=18
        )

        self.make_label(
            sidebar, "EVENT LOG",
            10, MUTED, True
        ).pack(anchor="w", padx=18, pady=(18, 7))

        self.log_text = tk.Text(
            sidebar,
            height=7,
            bg="#111A23",
            fg="#D5DFE8",
            insertbackground=WHITE,
            font=("Consolas", 9),
            relief="flat",
            wrap="word",
            padx=10,
            pady=8
        )
        self.log_text.pack(
            fill="both", expand=True,
            padx=18, pady=(0, 18)
        )
        self.log_text.insert(
            "end",
            "System initialized.\nWaiting for route request..."
        )
        self.log_text.config(state="disabled")

    def metric(self, parent, title, value):

        box = tk.Frame(parent, bg=PANEL_LIGHT)
        box.pack(
            side="left", fill="both",
            expand=True, padx=(0, 6)
        )

        self.make_label(
            box, title, 8, MUTED, True
        ).pack(anchor="w", padx=10, pady=(10, 4))

        value_label = self.make_label(
            box, value, 19, WHITE, True
        )
        value_label.pack(
            anchor="w", padx=10, pady=(0, 10)
        )

        return value_label

    # ===================== MAP DESIGN =====================

    def draw_map(self):

        canvas = self.map_canvas
        canvas.delete("all")

        width = max(canvas.winfo_width(), 650)
        height = max(canvas.winfo_height(), 450)

        # Subtle map grid
        for x in range(0, width, 35):
            canvas.create_line(
                x, 0, x, height,
                fill="#26343F", width=1
            )

        for y in range(0, height, 35):
            canvas.create_line(
                0, y, width, y,
                fill="#26343F", width=1
            )

        # Abstract node positions arranged like a road map

        positions = {
            "A": (0.08, 0.50),
            "B": (0.25, 0.20),
            "C": (0.43, 0.20),
            "D": (0.63, 0.20),
            "E": (0.25, 0.50),
            "F": (0.43, 0.50),
            "G": (0.63, 0.50),
            "H": (0.88, 0.50),
            "I": (0.25, 0.82),
            "J": (0.43, 0.82),
            "K": (0.63, 0.82),
            "L": (0.88, 0.82)
        }

        points = {
            node: (int(px * width), int(py * height))
            for node, (px, py) in positions.items()
        }

        # Decorative neighborhood blocks
        for x, y, w, h in [
            (0.04, 0.08, 0.16, 0.12),
            (0.38, 0.06, 0.11, 0.10),
            (0.60, 0.08, 0.15, 0.12),
            (0.08, 0.82, 0.15, 0.10),
            (0.39, 0.86, 0.12, 0.08),
            (0.68, 0.80, 0.13, 0.10),
        ]:
            x1, y1 = int(x * width), int(y * height)
            x2, y2 = int((x + w) * width), int((y + h) * height)

            canvas.create_rectangle(
                x1, y1, x2, y2,
                fill="#25333B",
                outline="#2D3D47",
                width=1
            )

        # Small area labels
        canvas.create_text(
            int(width * 0.18), int(height * 0.15),
            text="NORTH DISTRICT",
            fill="#526574",
            font=("Segoe UI", 8, "bold")
        )
        canvas.create_text(
            int(width * 0.80), int(height * 0.90),
            text="SOUTH DISTRICT",
            fill="#526574",
            font=("Segoe UI", 8, "bold")
        )

        drawn = set()

        for node in city.graph:
            for road in city.graph[node]:

                neighbor = road["node"]
                key = tuple(sorted((node, neighbor)))

                if key in drawn:
                    continue
                drawn.add(key)

                x1, y1 = points[node]
                x2, y2 = points[neighbor]

                # Base road
                canvas.create_line(
                    x1, y1, x2, y2,
                    fill=ROAD_EDGE,
                    width=15,
                    capstyle="round"
                )
                canvas.create_line(
                    x1, y1, x2, y2,
                    fill=ROAD,
                    width=10,
                    capstyle="round"
                )

                color = None
                route_width = 5

                if road["blocked"]:
                    color = RED
                    route_width = 7

                elif self.traffic_road == key:
                    color = ORANGE
                    route_width = 7

                if (
                    self.current_route
                    and node in self.current_route
                    and neighbor in self.current_route
                ):
                    i = self.current_route.index(node)
                    j = self.current_route.index(neighbor)

                    if abs(i - j) == 1:
                        color = BLUE
                        route_width = 7

                if color:
                    canvas.create_line(
                        x1, y1, x2, y2,
                        fill=color,
                        width=route_width,
                        capstyle="round"
                    )

                # Distance marker
                mx = (x1 + x2) // 2
                my = (y1 + y2) // 2

                canvas.create_rectangle(
                    mx - 13, my - 10,
                    mx + 13, my + 10,
                    fill="#17232D",
                    outline=""
                )
                canvas.create_text(
                    mx, my,
                    text=str(road["distance"]),
                    fill="#D8E2EA",
                    font=("Segoe UI", 8, "bold")
                )

        # Nodes and location markers
        for node, (x, y) in points.items():

            if node == self.start_node:
                fill = GREEN
                label = "EMERGENCY"

            elif node == self.goal_node:
                fill = "#E879A9"
                label = "HOSPITAL"

            else:
                fill = "#D7E1E9"
                label = node

            radius = 13

            canvas.create_oval(
                x - radius - 3, y - radius - 3,
                x + radius + 3, y + radius + 3,
                fill="#17232D",
                outline=fill,
                width=2
            )

            canvas.create_oval(
                x - radius, y - radius,
                x + radius, y + radius,
                fill=fill,
                outline=""
            )

            canvas.create_text(
                x, y,
                text=node,
                fill="#101820",
                font=("Segoe UI", 10, "bold")
            )

            if node in (self.start_node, self.goal_node):
                canvas.create_text(
                    x, y + 27,
                    text=label,
                    fill=fill,
                    font=("Segoe UI", 8, "bold")
                )

        # Map legend
        legend_y = height - 27
        legend_x = 20

        for color, label in [
            (BLUE, "A* Route"),
            (RED, "Blocked"),
            (ORANGE, "Traffic"),
            (GREEN, "Emergency"),
            ("#E879A9", "Hospital")
        ]:
            canvas.create_oval(
                legend_x, legend_y - 5,
                legend_x + 10, legend_y + 5,
                fill=color, outline=""
            )
            canvas.create_text(
                legend_x + 16, legend_y,
                text=label,
                fill=WHITE,
                anchor="w",
                font=("Segoe UI", 8)
            )
            legend_x += 105

    # ===================== EVENT HELPERS =====================

    def log(self, message):

        self.log_text.config(state="normal")
        self.log_text.insert("end", "\n" + message)
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    def update_status(self, scenario):

        if scenario == "Normal":
            self.status_badge.config(
                text="● SYSTEM READY", fg=GREEN
            )
            self.status_text.config(
                text="● NORMAL CONDITIONS", fg=GREEN
            )

        elif scenario == "Accident":
            self.status_badge.config(
                text="● INCIDENT DETECTED", fg=RED
            )
            self.status_text.config(
                text="● ROAD BLOCKED", fg=RED
            )

        else:
            self.status_badge.config(
                text="● TRAFFIC ALERT", fg=ORANGE
            )
            self.status_text.config(
                text="● HEAVY TRAFFIC", fg=ORANGE
            )

    def safe_database_call(self, function, *args):

        try:
            function(*args)
            return True
        except Exception as error:
            self.log("Database warning: " + str(error))
            return False
    
    def generate_random_obstacles(self, start, goal, original_path):

        # Collect each road once
        roads = []

        for node in city.graph:
            for road in city.graph[node]:
                neighbor = road["node"]

                if node < neighbor:
                    roads.append((node, neighbor))

        # Prefer roads on the original route, so obstacles
        # are more likely to cause a reroute.
        route_roads = [
            (original_path[i], original_path[i + 1])
            for i in range(len(original_path) - 1)
        ]

        random.shuffle(route_roads)

        # Try different combinations until a reachable,
        # different route is found.
        for _ in range(30):

            city.reset_conditions()

            count = random.randint(1, min(3, len(route_roads)))
            chosen = route_roads[:count]

            for a, b in chosen:
                city.block_road(a, b)

            new_path, new_cost = astar(
                city.graph, start, goal
            )

            if new_path and new_path != original_path:
                return chosen, new_path, new_cost

        # Fallback: block random roads while preserving
        # at least one possible route.
        for _ in range(30):

            city.reset_conditions()

            chosen = random.sample(
                roads,
                random.randint(1, min(3, len(roads)))
            )

            for a, b in chosen:
                city.block_road(a, b)

            new_path, new_cost = astar(
                city.graph, start, goal
            )

            if new_path:
                return chosen, new_path, new_cost

        city.reset_conditions()
        return [], original_path, float("inf")
    # ===================== ROUTING =====================

    def find_route(self):

        start = self.start_box.get()
        goal = self.goal_box.get()
        scenario = self.scenario_box.get()

        if start == goal:
            messagebox.showwarning(
                "Invalid selection",
                "Choose different emergency and hospital locations."
            )
            return

        # Reset the previous simulation
        city.reset_conditions()

        self.traffic_road = None
        self.start_node = start
        self.goal_node = goal
        self.current_route = []

        path, cost = astar(city.graph, start, goal)

        if not path:
            messagebox.showerror(
                "No route",
                "No route is currently available."
            )
            self.draw_map()
            return

        self.current_route = path
        reroutes = 0

        self.update_status("Normal")
        self.log(f"New request: {start} → {goal}")
        self.log("Initial route: " + " → ".join(path))
        self.log(f"Initial cost: {cost:.2f}")

        # Handle the selected event
        if scenario == "Random Obstacles":

            chosen, new_path, new_cost = (
                self.generate_random_obstacles(
                    start, goal, path
                )
            )

            if not chosen:
                self.log(
                    "Could not generate a valid alternative route."
                )
                self.draw_map()
                return

            for a, b in chosen:
                self.log(f"Road blocked: {a} → {b}")

                self.safe_database_call(
                    save_incident,
                    a,
                    b,
                    "OBSTACLE",
                    "Randomly generated road obstacle"
                )

            self.update_status("Accident")
            self.current_route = new_path
            path = new_path
            cost = new_cost
            reroutes = 1

            self.log(
                "A* found an alternative route: "
                + " → ".join(path)
            )

        elif scenario in ("Accident", "Heavy Traffic"):

            if len(path) < 2:
                self.log("No road segment available for the event.")
                return

            current = path[0]
            next_node = path[1]

            self.log("Event detected: " + scenario)

            if scenario == "Accident":

                accident(current, next_node)

                self.safe_database_call(
                    save_incident,
                    current,
                    next_node,
                    "ACCIDENT",
                    "Simulated accident blocked the road"
                )

            else:

                change_traffic(current, next_node, 5.0)

                self.traffic_road = tuple(
                    sorted((current, next_node))
                )

                self.safe_database_call(
                    save_incident,
                    current,
                    next_node,
                    "TRAFFIC",
                    "Simulated heavy traffic increased road cost"
                )

            self.update_status(scenario)
            self.draw_map()

            new_path, new_cost = astar(
                city.graph, start, goal
            )

            if not new_path:
                self.current_route = []
                self.draw_map()
                self.log("No alternative route is available.")
                self.route_text.config(
                    text="No alternative route available."
                )
                self.cost_value.config(text="—")
                return

            path = new_path
            cost = new_cost
            reroutes = 1
            self.current_route = path

            self.log("A* recalculated the route.")
            self.log("Updated route: " + " → ".join(path))
            self.log(f"Updated cost: {cost:.2f}")

        else:
            self.log("Normal conditions. No obstacles added.")

        # Update the UI
        self.draw_map()
        self.cost_value.config(text=f"{cost:.1f}")
        self.reroute_value.config(text=str(reroutes))
        self.route_text.config(text="  →  ".join(path))

        self.log("Route planning complete.")

        # Save the final route
        saved = self.safe_database_call(
            save_route,
            start,
            goal,
            path,
            cost,
            reroutes
        )

        if saved:
            self.log("Route history saved to MySQL.")
        else:
            self.log("Route shown, but database save failed.")
    # ===================== START =====================


if __name__ == "__main__":

    root = tk.Tk()
    app = EmergencyRouteApp(root)

    root.mainloop()
