#!/usr/bin/env python3
from __future__ import annotations

import sys
import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Dict, List, Tuple
from collections import OrderedDict, deque

@dataclass
class Task:
    """Represents a single task with a name, duration, and dependencies."""
    name: str
    duration_seconds: float
    deps: List[str]


@dataclass
class TaskSet:
    """A collection of tasks, preserving their declaration order."""
    tasks: Dict[str, Task]
    order: List[str]

    def __iter__(self):
        """Iterate over tasks in the declared order."""
        for name in self.order:
            yield self.tasks[name]


def _parse_deps(fields: List[str]):
    """
    Parse dependencies from CSV fields starting at index 2.
    Removes duplicates and preserves order.
    """
    if len(fields) < 3:
        return []
    dep_field = ",".join(fields[2:]).strip()
    if not dep_field or dep_field == "-":
        return []
    seen = set()
    ordered: List[str] = []
    for token in dep_field.split(","):
        dep = token.strip()
        if dep and dep not in seen:
            seen.add(dep)
            ordered.append(dep)
    return ordered


def parse_task_line(line: str):
    """
    Parse a single line from the text file into a Task object.
    Skips comments (#) and blank lines.
    """
    raw = line.strip()
    if not raw or raw.startswith("#"):
        print("Skipping line:", line.rstrip(), flush=True)
        return None

    fields = [field.strip() for field in raw.split(",")]
    print("Fields parsed:", fields, flush=True)

    name = fields[0]
    duration = float(fields[1])
    deps = _parse_deps(fields)
    print(f"Created Task: name={name}, duration={duration}, deps={deps}", flush=True)
    return Task(name=name, duration_seconds=duration, deps=deps)


def load_tasks_from_text(path: Path):
    """
    Load all tasks from a text file into a TaskSet.
    Maintains insertion order and ensures unique task names.
    """
    print("Loading tasks from:", path, flush=True)
    by_name: "OrderedDict[str, Task]" = OrderedDict()
    order: List[str] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            print("Reading line:", line.rstrip(), flush=True)
            task = parse_task_line(line)
            if task is None:
                continue
            by_name[task.name] = task
            order.append(task.name)
            print(f"Task '{task.name}' added to TaskSet.", flush=True)
    print("Total tasks loaded:", len(by_name), flush=True)
    return TaskSet(tasks=dict(by_name), order=order)

def validate_tasks(ts: TaskSet):
    """
    Validate a TaskSet for:
    - Non-negative durations
    - No self-dependencies
    - All dependencies existing
    - No cycles in the dependency graph
    """
    errors: List[str] = []

    # Basic checks
    for t in ts.tasks.values():
        if t.duration_seconds < 0:
            errors.append(f"Task '{t.name}': duration must be non-negative.")
        for d in t.deps:
            if d == t.name:
                errors.append(f"Task '{t.name}': cannot depend on itself.")
            if d not in ts.tasks:
                errors.append(f"Task '{t.name}': dependency '{d}' not found.")

    # Cycle detection using DFS
    WHITE, GRAY, BLACK = 0, 1, 2  # colors for DFS state
    color: Dict[str, int] = {name: WHITE for name in ts.tasks}

    def dfs(u: str, stack: List[str]) -> bool:
        """Recursive DFS to detect cycles."""
        color[u] = GRAY
        stack.append(u)
        for v in ts.tasks[u].deps:
            if color[v] == WHITE:
                if not dfs(v, stack):
                    return False
            elif color[v] == GRAY:
                cycle = stack[stack.index(v):] + [v]
                errors.append("Cycle detected: " + " -> ".join(cycle))
                return False
        color[u] = BLACK
        stack.pop()
        return True

    # Start DFS from all unvisited nodes
    for name in ts.tasks:
        if color[name] == WHITE:
            dfs(name, [])

    return errors


def topo_order(ts: TaskSet):
    """
    Return a topological ordering of tasks.
    """
    # Compute indegrees
    indeg: Dict[str, int] = {n: 0 for n in ts.tasks}
    for t in ts.tasks.values():
        for d in t.deps:
            indeg[t.name] += 1

    # Start with all nodes with indegree 0
    q = deque([n for n, deg in indeg.items() if deg == 0])

    # Reverse adjacency list: dep -> list of dependents
    adj_rev: Dict[str, List[str]] = {n: [] for n in ts.tasks}
    for t in ts.tasks.values():
        for d in t.deps:
            adj_rev[d].append(t.name)

    # Generate ordering
    order: List[str] = []
    while q:
        u = q.popleft()
        order.append(u)
        for v in adj_rev[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    return order


def expected_total_runtime(ts: TaskSet):
    """
    Compute the expected total runtime (critical path length).
    Also returns earliest start (es) and earliest finish (ef) times for each task.
    """
    order = topo_order(ts)
    es: Dict[str, float] = {n: 0.0 for n in ts.tasks}  # earliest start
    ef: Dict[str, float] = {n: 0.0 for n in ts.tasks}  # earliest finish

    for n in order:
        t = ts.tasks[n]
        if t.deps:
            max_finish = max(ef[d] for d in t.deps)
            es[n] = max_finish
        else:
            es[n] = 0.0
        ef[n] = es[n] + t.duration_seconds

    makespan = max(ef.values())
    return makespan, es, ef


def build_arg_parser():
    """Build the argument parser with subcommands."""
    parser = argparse.ArgumentParser(
        description="Parse, validate, and estimate runtime for a text task list."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # 'print' subcommand
    p_print = sub.add_parser("print", help="Parse and print tasks")
    p_print.add_argument("task_file", type=Path, help="Path to the task list")

    # 'validate' subcommand
    p_val = sub.add_parser("validate", help="Validate and output expected total runtime (no execution)")
    p_val.add_argument("task_file", type=Path, help="Path to the task list")
    p_val.add_argument("--plan", action="store_true", help="Also print earliest start/finish per task")

    return parser


def main(argv: Iterable[str] | None = None):
    """
    Entry point for the CLI tool.
    Supports 'print' and 'validate' subcommands.
    Defaults to 'print' if only a .txt file is given.
    """
    if argv is None:
        argv = sys.argv[1:]
    argv = list(argv)

    # Auto-inject 'print' if user just runs: main.py file.txt
    if len(argv) >= 1:
        first = str(argv[0])
        if first not in ("print", "validate") and first.endswith(".txt"):
            argv = ["print"] + argv

    parser = build_arg_parser()
    args = parser.parse_args(argv)

    # Handle 'print'
    if args.command == "print":
        task_set = load_tasks_from_text(args.task_file)
        print("Loaded", len(task_set.tasks), "task(s) from", args.task_file, ":", flush=True)
        for t in task_set:
            deps_str = ", ".join(t.deps) if t.deps else "-"
            print(f"  - {t.name}: duration={t.duration_seconds}s, deps=[{deps_str}]", flush=True)
        return 0

    # Handle 'validate'
    if args.command == "validate":
        ts = load_tasks_from_text(args.task_file)
        errs = validate_tasks(ts)
        if errs:
            print("Validation errors found:", flush=True)
            for e in errs:
                print("  - " + e, flush=True)
            return 2
        expected, es, ef = expected_total_runtime(ts)
        print("Validation OK.", flush=True)
        print(f"Expected total runtime (critical path): {expected:.3f} seconds", flush=True)
        if args.plan:
            order = topo_order(ts)
            print("\nPlan (earliest start -> finish):", flush=True)
            for n in order:
                deps_str = ", ".join(ts.tasks[n].deps) if ts.tasks[n].deps else "-"
                print(f"  {n}: start {es[n]:.3f}s, finish {ef[n]:.3f}s, "
                      f"duration {ts.tasks[n].duration_seconds}s, deps={deps_str}", flush=True)
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
