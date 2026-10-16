import matplotlib.pyplot as plt
import networkx as nx
import streamlit as st

from map_data import ADJACENCY, POSITIONS, COLOR_PALETTE, COLOR_LABELS
from solver import solve_backtracking, solve_sat, validate_coloring

st.set_page_config(
    page_title="Map Coloring Solver",
    page_icon="🎨",
    layout="wide",
)

st.title("🎨 Map Coloring Using Graph Coloring")
st.caption(
    "Constraint satisfaction with Backtracking and SAT solvers"
)




def build_graph(adjacency):
    graph = nx.Graph()
    graph.add_nodes_from(adjacency.keys())
    for node, neighbors in adjacency.items():
        for neighbor in neighbors:
            graph.add_edge(node, neighbor)
    return graph


def draw_graph(adjacency, coloring=None, title="Region adjacency graph"):
    graph = build_graph(adjacency)
    node_colors = []
    for node in graph.nodes:
        if coloring is None or node not in coloring:
            node_colors.append("#d5d8dc")
        else:
            node_colors.append(COLOR_PALETTE[coloring[node] % len(COLOR_PALETTE)])

    fig, ax = plt.subplots(figsize=(9, 5.5))
    nx.draw_networkx(
        graph,
        pos=POSITIONS,
        ax=ax,
        labels={node: node for node in graph.nodes},
        node_color=node_colors,
        node_size=2200,
        font_size=11,
        font_weight="bold",
        edge_color="#616a6b",
        width=2,
        linewidths=1.5,
    )
    ax.set_title(title, fontsize=14)
    ax.axis("off")
    fig.tight_layout()
    return fig


with st.sidebar:
    st.header("Solver settings")
    number_of_colors = st.slider(
        "Number of available colors",
        min_value=1,
        max_value=7,
        value=3,
        help="Choose how many different colors the solver can use.",
    )
    solver_choice = st.radio(
        "Algorithm",
        ["Backtracking", "SAT (PySAT)", "Compare both"],
    )
    st.divider()
    st.subheader("Color palette")
    for i in range(number_of_colors):
        st.markdown(
            f'<span style="display:inline-block;width:14px;height:14px;'
            f'background:{COLOR_PALETTE[i]};border-radius:3px;'
            f'margin-right:8px;"></span>{COLOR_LABELS[i]}',
            unsafe_allow_html=True,
        )

tab1, tab2, tab3 = st.tabs(
    ["Color the graph", "Graph data", "How it works"]
)

with tab1:
    left, right = st.columns([1.2, 1])
    with left:
        st.subheader("Current graph")
        st.pyplot(draw_graph(ADJACENCY), use_container_width=True)

    with right:
        st.subheader("Run solver")
        st.write(f"**Regions:** {len(ADJACENCY)}")
        edge_count = sum(len(v) for v in ADJACENCY.values()) // 2
        st.write(f"**Borders (edges):** {edge_count}")
        run_clicked = st.button(
            "🎨 Solve map coloring",
            type="primary",
            use_container_width=True,
        )

    if run_clicked:
        results = {}

        if solver_choice in ("Backtracking", "Compare both"):
            results["Backtracking"] = solve_backtracking(
                ADJACENCY, number_of_colors
            )

        if solver_choice in ("SAT (PySAT)", "Compare both"):
            results["SAT"] = solve_sat(ADJACENCY, number_of_colors)

        st.divider()
        st.subheader("Results")

        for algorithm, result in results.items():
            st.markdown(f"### {algorithm}")
            if result["success"]:
                st.success(result["message"])
                coloring = result["coloring"]

                metrics = st.columns(4)
                metrics[0].metric(
                    "Regions colored", len(coloring)
                )
                metrics[1].metric(
                    "Colors used", len(set(coloring.values()))
                )
                metrics[2].metric(
                    "Execution time",
                    f'{result["elapsed_seconds"] * 1000:.3f} ms',
                )
                if result["backtracks"] is not None:
                    metrics[3].metric(
                        "Backtracks", result["backtracks"]
                    )
                else:
                    metrics[3].metric(
                        "SAT clauses", result["attempts"]
                    )

                if validate_coloring(ADJACENCY, coloring):
                    st.success(
                        "Validation passed: no adjacent regions share a color."
                    )
                else:
                    st.error("Validation failed. Check the solver.")

                st.pyplot(
                    draw_graph(
                        ADJACENCY,
                        coloring,
                        f"{algorithm} solution ({len(set(coloring.values()))} colors)",
                    ),
                    use_container_width=True,
                )

                assignments = [
                    {
                        "Region": node,
                        "Color": COLOR_LABELS[color],
                        "Color index": color + 1,
                    }
                    for node, color in coloring.items()
                ]
                st.dataframe(assignments, use_container_width=True, hide_index=True)
            else:
                st.error(result["message"])
                st.caption(
                    f'Elapsed time: {result["elapsed_seconds"] * 1000:.3f} ms'
                )

        if len(results) == 2:
            st.divider()
            st.subheader("Algorithm comparison")
            comparison_rows = []
            for algorithm, result in results.items():
                comparison_rows.append({
                    "Algorithm": algorithm,
                    "Solution found": "Yes" if result["success"] else "No",
                    "Execution time (ms)": round(
                        result["elapsed_seconds"] * 1000, 4
                    ),
                    "Attempts / clauses": result["attempts"],
                    "Backtracks": (
                        result["backtracks"]
                        if result["backtracks"] is not None else "N/A"
                    ),
                })
            st.dataframe(
                comparison_rows,
                use_container_width=True,
                hide_index=True,
            )
            st.caption(
                "Runtime depends on your computer and solver overhead. "
                "One run is not enough to conclude which algorithm is faster."
            )

with tab2:
    st.subheader("Adjacency list")
    st.write(
        "Each region is a node. Each listed neighbor shares a border "
        "with that region. Every border should be represented in both directions."
    )
    rows = [
        {"Region": region, "Adjacent regions": ", ".join(neighbors) or "None"}
        for region, neighbors in ADJACENCY.items()
    ]
    st.dataframe(rows, use_container_width=True, hide_index=True)
    st.subheader("Graph view")
    st.pyplot(draw_graph(ADJACENCY), use_container_width=True)

with tab3:
    st.subheader("Backtracking")
    st.markdown(
        """
        1. Select an uncolored region.
        2. Try each available color.
        3. Reject a color if a neighbor already has it.
        4. Continue with the next region when the choice is valid.
        5. If no color works, undo the previous assignment and try another.
        """
    )
    st.subheader("SAT formulation")
    st.markdown(
        r"""
        Define a Boolean variable \(X_{v,c}\) meaning region \(v\) uses color \(c\).

        - **At least one color:** each region must have at least one true color variable.
        - **At most one color:** no region can have two true color variables.
        - **Neighbor constraint:** for every adjacent pair \(u,v\) and color \(c\),
          add \(\neg X_{u,c} \lor \neg X_{v,c}\).
        """
    )
    st.subheader("Important limitation")
    st.write(
        "The supplied graph is for algorithm demonstration. For a real map, "
        "obtain a suitable GeoJSON boundary dataset and construct adjacency "
        "from shared polygon boundaries before plotting the geographic regions."
    )

st.divider()
st.caption(
    "Educational project only. The graph data is illustrative and can be "
    "replaced with verified geographic adjacency data."
)
