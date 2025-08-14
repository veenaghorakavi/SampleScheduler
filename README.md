# SampleScheduler
Python-based solution for a command line tool to schedule and optionally run a series of tasks in parallel.

## Current Status
- Implemented core data model for representing tasks and their dependencies.
- Added parsing utilities to read a text task list and load it into the data model.
- Integrated command-line interface with subcommands.
- Added detailed debug prints for real-time feedback during parsing.
- Implemented validation checks for negative durations, missing dependencies, self-dependencies, and cycles.
- Added critical-path runtime estimation.
- Implemented parallel task execution with actual runtime measurement and comparison to expected runtime.

## Core Data Model
Each task is represented by a name, a duration in seconds, and an optional list of dependencies. The task set is stored as a graph where nodes represent tasks and edges represent dependency relationships.

## How to run
The sample test file is provided as test.txt. 

The first command parses the task file and displays each task with its duration and dependencies. This explicitly runs parsed tasks from the file.

```bash
python3 main.py print test.txt
```
The second command does what the first command does and is the default if the user does not provide any input. This implicity runs parsed tasks from the file. 

```bash
python3 main.py test.txt
```

The third command validates and shows the total run time.

```bash
python3 main.py validate test.txt
```

The fourth command extends the functionality of the prior command by printing the earliest start and finish times for each task in topological order.

```bash
python3 main.py validate test.txt --plan
```

The fifth command runs tasks in parallel and compares actual and expected run times. Please note the provided test file takes ~17 minutes.

```bash
python3 main.py run test.txt
```

The sixth command runs tasks with limited concurrency. This example shows four workers. 

```bash
python3 main.py run test.txt --max-workers 4
```
