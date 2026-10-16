"""Graph-coloring solvers: backtracking and SAT (PySAT)."""

from time import perf_counter


def validate_graph(adjacency):
    """Check that all neighbors exist and adjacency is symmetric."""
    nodes = set(adjacency)
    for node, neighbors in adjacency.items():
        for neighbor in neighbors:
            if neighbor not in nodes:
                raise ValueError(
                    f"'{node}' lists unknown neighbor '{neighbor}'."
                )
            if node not in adjacency[neighbor]:
                raise ValueError(
                    f"Adjacency must be symmetric: '{node}' lists "
                    f"'{neighbor}', but not vice versa."
                )


def validate_coloring(adjacency, coloring):
    """Return True only if every node is colored and every edge is valid."""
    if coloring is None or set(coloring) != set(adjacency):
        return False
    for node, neighbors in adjacency.items():
        for neighbor in neighbors:
            if coloring[node] == coloring[neighbor]:
                return False
    return True


def solve_backtracking(adjacency, number_of_colors):
    """Solve graph coloring with MRV-style variable ordering and backtracking.

    Returns a dictionary with:
      success, coloring, elapsed_seconds, attempts, backtracks, message
    """
    validate_graph(adjacency)
    start = perf_counter()

    if number_of_colors < 1:
        return {
            "success": False, "coloring": None,
            "elapsed_seconds": perf_counter() - start,
            "attempts": 0, "backtracks": 0,
            "message": "The number of colors must be at least 1.",
        }

    nodes = list(adjacency.keys())
    coloring = {}
    attempts = 0
    backtracks = 0

    def choose_next_node():
        uncolored = [node for node in nodes if node not in coloring]
        if not uncolored:
            return None

        # Minimum Remaining Values (MRV): choose the node with the fewest
        # currently legal colors. Degree is used as a tie-breaker.
        def sort_key(node):
            forbidden = {
                coloring[n]
                for n in adjacency[node]
                if n in coloring
            }
            legal_count = number_of_colors - len(forbidden)
            return (legal_count, -len(adjacency[node]))

        return min(uncolored, key=sort_key)

    def backtrack():
        nonlocal attempts, backtracks

        if len(coloring) == len(nodes):
            return True

        node = choose_next_node()
        used_by_neighbors = {
            coloring[n] for n in adjacency[node] if n in coloring
        }

        for color in range(number_of_colors):
            attempts += 1
            if color in used_by_neighbors:
                continue

            coloring[node] = color

            # Forward check: every remaining node must have at least one
            # color not already used by its colored neighbors.
            possible = True
            for other in nodes:
                if other in coloring:
                    continue
                forbidden = {
                    coloring[n] for n in adjacency[other] if n in coloring
                }
                if len(forbidden) >= number_of_colors:
                    possible = False
                    break

            if possible and backtrack():
                return True

            del coloring[node]
            backtracks += 1

        return False

    success = backtrack()
    elapsed = perf_counter() - start

    result_coloring = dict(coloring) if success else None
    return {
        "success": success,
        "coloring": result_coloring,
        "elapsed_seconds": elapsed,
        "attempts": attempts,
        "backtracks": backtracks,
        "message": (
            "A valid coloring was found."
            if success else
            f"No valid coloring exists with {number_of_colors} color(s)."
        ),
    }


def solve_sat(adjacency, number_of_colors):
    """Solve graph coloring as SAT using python-sat (PySAT).

    Each Boolean variable X(node, color) means that node uses that color.
    Returns the same result structure as solve_backtracking.
    """
    validate_graph(adjacency)
    start = perf_counter()

    if number_of_colors < 1:
        return {
            "success": False, "coloring": None,
            "elapsed_seconds": perf_counter() - start,
            "attempts": 0, "backtracks": 0,
            "message": "The number of colors must be at least 1.",
        }

    try:
        from pysat.solvers import Solver
    except ImportError:
        return {
            "success": False, "coloring": None,
            "elapsed_seconds": perf_counter() - start,
            "attempts": 0, "backtracks": 0,
            "message": (
                "PySAT is not installed. Run: "
                "python -m pip install python-sat"
            ),
        }

    nodes = list(adjacency.keys())
    node_index = {node: i for i, node in enumerate(nodes)}

    # Variables are numbered from 1; zero is not a valid SAT variable.
    def variable(node, color):
        return node_index[node] * number_of_colors + color + 1

    clauses = []

    for node in nodes:
        # At least one color must be selected for each node.
        clauses.append([
            variable(node, color)
            for color in range(number_of_colors)
        ])

        # At most one color per node (pairwise encoding).
        for c1 in range(number_of_colors):
            for c2 in range(c1 + 1, number_of_colors):
                clauses.append([
                    -variable(node, c1),
                    -variable(node, c2),
                ])

    # Adjacent nodes cannot use the same color.
    for node, neighbors in adjacency.items():
        for neighbor in neighbors:
            if node_index[node] >= node_index[neighbor]:
                continue  # add each undirected edge once
            for color in range(number_of_colors):
                clauses.append([
                    -variable(node, color),
                    -variable(neighbor, color),
                ])

    coloring = None
    with Solver(name="g3", bootstrap_with=clauses) as sat_solver:
        satisfiable = sat_solver.solve()
        if satisfiable:
            model = set(sat_solver.get_model())
            coloring = {}
            for node in nodes:
                for color in range(number_of_colors):
                    if variable(node, color) in model:
                        coloring[node] = color
                        break

    elapsed = perf_counter() - start
    success = coloring is not None and validate_coloring(adjacency, coloring)

    return {
        "success": success,
        "coloring": coloring if success else None,
        "elapsed_seconds": elapsed,
        "attempts": len(clauses),
        "backtracks": None,
        "message": (
            "A valid coloring was found by SAT."
            if success else
            f"No valid coloring exists with {number_of_colors} color(s)."
        ),
    }
