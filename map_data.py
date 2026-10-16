"""Sample graph data for the Map Coloring project.

The graph represents adjacency between Australian states/territories.
It is a schematic graph, not geographic boundary data.
"""

ADJACENCY = {
    "WA": ["NT", "SA"],
    "NT": ["WA", "SA", "QLD"],
    "SA": ["WA", "NT", "QLD", "NSW", "VIC"],
    "QLD": ["NT", "SA", "NSW"],
    "NSW": ["QLD", "SA", "VIC"],
    "VIC": ["SA", "NSW"],
    "TAS": [],
}

# Schematic positions for displaying the graph.
POSITIONS = {
    "WA": (0.0, 2.0),
    "NT": (1.6, 3.0),
    "SA": (1.6, 1.5),
    "QLD": (3.2, 3.0),
    "NSW": (3.3, 1.8),
    "VIC": (2.9, 0.7),
    "TAS": (4.1, 0.0),
}

COLOR_PALETTE = [
    "#e74c3c",  # red
    "#3498db",  # blue
    "#f1c40f",  # yellow
    "#2ecc71",  # green
    "#9b59b6",  # purple
    "#e67e22",  # orange
    "#1abc9c",  # turquoise
]

COLOR_LABELS = [
    "Red", "Blue", "Yellow", "Green",
    "Purple", "Orange", "Turquoise"
]
