# Map Coloring Using Backtracking and SAT

A Python + Streamlit educational project demonstrating graph coloring as a
constraint-satisfaction problem.

## Features

- Backtracking graph-coloring solver with variable ordering and forward checking
- SAT encoding solved using PySAT
- Adjustable number of colors
- Graph visualization and validation
- Runtime and solver-statistics comparison
- Sample adjacency graph for Australian states and territories

> The included graph and drawing are schematic, not a geographically accurate map.
> For a real map, use a verified GeoJSON dataset and derive adjacency from polygon
> boundaries.

## Requirements

- Python 3.10 or newer recommended
- VS Code (optional)
- Internet access to install packages

## Windows setup (PowerShell)

```powershell
cd map-coloring-project
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m streamlit run app.py
```

If PowerShell prevents virtual-environment activation, run the environment's
Python directly:

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe -m streamlit run app.py
```

The app normally opens at http://localhost:8501.

## Test cases

- 1 color: the graph should not be colorable.
- 2 colors: the graph should not be colorable because it contains triangles.
- 3 colors: a valid coloring should be found.
- 4 colors: a valid coloring should be found.

## Files

- `app.py`: Streamlit user interface and visualization
- `solver.py`: Backtracking and SAT solvers
- `map_data.py`: Example adjacency graph, positions, and palette
- `requirements.txt`: Python dependencies

## SAT encoding

For every region `v` and color `c`, define Boolean variable `X(v,c)`.

1. At least one color per region.
2. At most one color per region.
3. For every border `(u,v)` and color `c`, add
   `not X(u,c) OR not X(v,c)`.

## Extension ideas

- Replace the sample graph with Kerala districts or Indian states.
- Load GeoJSON and render actual polygon shapes with GeoPandas.
- Add algorithm step-by-step animation.
- Repeat benchmark runs and report mean runtime.
- Compare different backtracking heuristics.
