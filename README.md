# SampleScheduler
Python-based solution for a command line tool to schedule and optionally run a series of tasks in parallel.

Current Status

- Implemented core data model for representing tasks and their dependencies.
- Added parsing utilities to read a text task list and load it into the data model.
- CLI integration using argparse.
- Added detailed debug prints for real-time feedback while parsing.


Plan of action:
1. Create data model
2. Add parsing utilities
3. Add validation
4. Compute run time for the edge of the data model
5. Clean up

Core data model (For documentation):

Task {
    name: str
    duration: float
    dependencies: List(str)
}

Graph {
    nodes: name -> Task
    edges : dependecies -> Task
}