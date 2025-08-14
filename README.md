# SampleScheduler
Python-based solution for a command line tool to schedule and optionally run a series of tasks in parallel.

Plan of action:
Create a file with sample inputs.
Create a main file with the scheduler.

Core data model:

Task {
    name: str
    duration: float
    dependencies: [str] -> list of strings
}

Graph {
    nodes: name -> Task
    edges : dependecies -> Task
}