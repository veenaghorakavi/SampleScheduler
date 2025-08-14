# SampleScheduler
Python-based solution for a command line tool to schedule and optionally run a series of tasks in parallel.

## Current Status

- Implemented core data model for representing tasks and their dependencies.
- Added parsing utilities to read a text task list and load it into the data model.
- Integrated command-line interface using with subcommands.
- Added detailed debug prints for real-time feedback during parsing.
- Implemented validation checks for negative durations, missing dependencies, self-dependencies, and cycles.
- Added critical-path runtime estimation.


## Plan of action:
1. Create data model
2. Add parsing utilities
3. Add validation
4. Compute run time for the edge of the data model
5. Clean up

## Core data model (For documentation):

Task {
    name: str
    duration: float
    dependencies: List(str)
}

Graph {
    nodes: name -> Task
    edges : dependecies -> Task
}

## How to run
The sample test file is provided as test.txt. 

The first command parses the task file and displays each task with its duration and dependencies.

```bash
python3 main.py print test.txt
```
The second command does what the first command does and is the default if the user does not provide any input.
```bash
python3 main.py test.txt
```

The third command validates the task list for negative durations, self-dependencies, missing dependencies, and cycles in the dependency graph. Also computes the expected total runtime using the critical path method.

```bash
python3 main.py validate test.txt
```

The fourth command extends the functionality of the prior command by printing the earliest start and finish times for each task in topological order.

```bash
python3 main.py validate test.txt --plan
```